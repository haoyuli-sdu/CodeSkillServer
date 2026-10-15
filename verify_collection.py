#!/usr/bin/env python3
"""Validate the checked-in CSS-993 release and its integrity manifest."""

from __future__ import annotations

import hashlib
import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COLLECTION = ROOT / "skill_collection"
MANIFEST = COLLECTION / "manifest.json"
EXPECTED = {
    "Application Components": 116,
    "Code Migration": 40,
    "Data & Infrastructure": 144,
    "General & Functional Code": 290,
    "Testing": 117,
    "Tools, SDKs & Generators": 189,
    "Web & API": 97,
}
FRONTMATTER_FIELD = re.compile(r"^(name|description)\s*:\s*.+$", re.MULTILINE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="rewrite skill_collection/manifest.json from the validated files",
    )
    args = parser.parse_args()
    errors: list[str] = []
    records: list[dict[str, str]] = []
    actual: dict[str, int] = {}

    category_dirs = {path.name: path for path in COLLECTION.iterdir() if path.is_dir()}
    unexpected = sorted(set(category_dirs) - set(EXPECTED))
    missing = sorted(set(EXPECTED) - set(category_dirs))
    if unexpected:
        errors.append(f"unexpected category directories: {unexpected}")
    if missing:
        errors.append(f"missing category directories: {missing}")

    for category, expected_count in EXPECTED.items():
        category_dir = COLLECTION / category
        skill_dirs = sorted(
            (path for path in category_dir.iterdir() if path.is_dir()),
            key=lambda path: path.name.casefold(),
        ) if category_dir.is_dir() else []
        actual[category] = len(skill_dirs)
        if len(skill_dirs) != expected_count:
            errors.append(
                f"{category}: expected {expected_count} skill directories, found {len(skill_dirs)}"
            )

        for skill_dir in skill_dirs:
            skill_files = list(skill_dir.glob("SKILL.md"))
            if len(skill_files) != 1:
                errors.append(f"{skill_dir}: expected exactly one SKILL.md")
                continue
            skill_file = skill_files[0]
            try:
                text = skill_file.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"{skill_file}: not valid UTF-8 ({exc})")
                continue
            if not text.startswith("---"):
                errors.append(f"{skill_file}: missing YAML frontmatter")
            fields = {match.group(1) for match in FRONTMATTER_FIELD.finditer(text)}
            if fields != {"name", "description"}:
                errors.append(f"{skill_file}: missing name or description frontmatter")
            records.append(
                {
                    "category": category,
                    "skill": skill_dir.name,
                    "path": skill_file.relative_to(ROOT).as_posix(),
                    "sha256": sha256(skill_file),
                }
            )

    if len(records) != 993:
        errors.append(f"expected 993 valid skill records, found {len(records)}")

    generated_manifest = {
        "schema_version": 1,
        "total_skills": len(records),
        "category_counts": actual,
        "skills": records,
    }
    if args.write_manifest and not errors:
        MANIFEST.write_text(
            json.dumps(generated_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if not MANIFEST.is_file():
        errors.append(f"missing manifest: {MANIFEST}")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest_records = manifest.get("skills", [])
        if manifest.get("total_skills") != 993:
            errors.append("manifest total_skills is not 993")
        if manifest.get("category_counts") != EXPECTED:
            errors.append("manifest category_counts do not match the release counts")
        if manifest_records != records:
            errors.append("manifest skill inventory or hashes do not match the collection")

    summary = {
        "status": "pass" if not errors else "fail",
        "total_skills": len(records),
        "category_counts": actual,
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

