#!/usr/bin/env python3
"""Export database Skills into standard folder-based Skill packages.

Output layout:
  output_dir/
    <category>/
      <safe-skill-name>/
        SKILL.md
    manifest.json

By default only confirmed_direct records with downloaded content are exported.
The classifier is run from the database, so no CSV input is required. The
classifier's fine-grained subtypes are folded into seven publication-level
categories, so the output contains no subtype directories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from . import direct_codegen_filter_v2 as classifier
except ImportError:  # Supports direct execution: python scripts/export_skills_as_folders.py
    import direct_codegen_filter_v2 as classifier

VERSION = "export-skills-as-folders-v2.0"
SKILL_FILENAME = "SKILL.md"

SQL = """
SELECT o.occurrence_id,o.source,o.external_id,o.title,o.repo_url,o.path,
       o.page_url,o.content_sha256,o.metadata_json,
       COALESCE(c.frontmatter_json,''),COALESCE(c.body,'')
FROM occurrences o
LEFT JOIN contents c ON o.content_sha256=c.content_sha256
ORDER BY o.source,o.occurrence_id
"""

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTISPACE = re.compile(r"\s+")
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


PLOT_CATEGORY_ORDER = [
    ("tools_sdks_generators", "01_Tools_SDKs_Generators", "Tools, SDKs & Generators", {
        "generator_metaprogramming", "cli_sdk_client_plugin",
    }),
    ("general_functional_code", "02_General_Functional_Code", "General & Functional Code", {
        "general_explicit", "function_method_algorithm", "specialized_executable",
    }),
    ("data_infrastructure", "03_Data_Infrastructure", "Data & Infrastructure", {
        "crud_database", "infra_config",
    }),
    ("testing", "04_Testing", "Testing", {"test_code"}),
    ("application_components", "05_Application_Components", "Application Components", {
        "class_module_model", "full_app_scaffold",
    }),
    ("web_api", "06_Web_API", "Web & API", {"frontend_ui", "backend_api"}),
    ("code_migration", "07_Code_Migration", "Code Migration", {"code_conversion_migration"}),
]
PLOT_CATEGORY_BY_KEY = {
    key: {"key": key, "folder": folder, "label": label, "subtypes": subtypes}
    for key, folder, label, subtypes in PLOT_CATEGORY_ORDER
}
SUBTYPE_TO_PLOT_CATEGORY = {
    subtype: category["key"]
    for category in PLOT_CATEGORY_BY_KEY.values()
    for subtype in category["subtypes"]
}
DEFAULT_PLOT_CATEGORY = "general_functional_code"

def utcnow():
    return datetime.now(timezone.utc).isoformat()


def parse_dict(value):
    try:
        obj = json.loads(value or "{}")
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def connect_readonly(path):
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise SystemExit(f"Database not found: {resolved}")
    return sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)


def provenance(db, source, external_id):
    try:
        rows = db.execute(
            """SELECT query_id,query_text,query_group,query_tier,MIN(rank),route
               FROM discovery_hits
               WHERE source=? AND external_id=?
               GROUP BY query_id,query_text,query_group,query_tier,route
               ORDER BY MIN(rank)""",
            (source, external_id),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [
        {"query_id": row[0], "query_text": row[1], "query_group": row[2],
         "query_tier": row[3], "rank": row[4], "route": row[5]}
        for row in rows
    ]


def safe_folder_name(value):
    """Make a portable, readable directory name without path traversal."""
    value = str(value or "").strip()
    value = value.replace("\u200b", "")
    value = INVALID_CHARS.sub("_", value)
    value = MULTISPACE.sub(" ", value)
    value = value.strip(" .")
    if not value:
        value = "unnamed-skill"
    if value.upper() in WINDOWS_RESERVED:
        value = "_" + value
    return value[:120]


def yaml_string(value):
    """A JSON double-quoted string is also a valid YAML double-quoted scalar."""
    return json.dumps(str(value or ""), ensure_ascii=False)


def plot_category(record):
    """Return the seven-category bucket for a classifier record."""
    subtype = record.get("classification", {}).get("subtype", "") or "unknown"
    key = SUBTYPE_TO_PLOT_CATEGORY.get(subtype, DEFAULT_PLOT_CATEGORY)
    category = PLOT_CATEGORY_BY_KEY[key]
    return category, subtype


def category_folder(record):
    return plot_category(record)[0]["folder"]

def fallback_name(title, slug, path, occurrence_id):
    if title and str(title).strip():
        return str(title).strip()
    if slug and str(slug).strip():
        return str(slug).strip()
    parts = str(path or "").replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[-1].lower() == "skill.md":
        return parts[-2]
    return f"imported-skill-{occurrence_id}"


def fallback_description(source, repo_url, path):
    # This is deliberately provenance text, not an invented semantic description.
    location = ": ".join(x for x in [repo_url, path] if x)
    return f"Imported Skill from {source}{(' (' + location + ')') if location else ''}; original description unavailable."


def skill_markdown(name, description, body):
    return "---\n" + f"name: {yaml_string(name)}\n" + f"description: {yaml_string(description)}\n" + "---\n\n" + (body or "").lstrip() + "\n"


def read_rows(db):
    for row in db.execute(SQL):
        occurrence_id, source, external_id, title, repo_url, path, page_url, content_hash, metadata_json, frontmatter_json, body = row
        frontmatter = parse_dict(frontmatter_json)
        metadata = parse_dict(metadata_json)
        prov = provenance(db, source, external_id)
        result = classifier.classify(title or "", "", frontmatter_json or "", body or "", bool(content_hash), prov)
        original_name = str(frontmatter.get("name") or fallback_name(title, metadata.get("slug", ""), path, occurrence_id)).strip()
        description = str(frontmatter.get("description") or fallback_description(source, repo_url, path)).strip()
        yield {
            "occurrence_id": occurrence_id,
            "source": source or "",
            "external_id": external_id or "",
            "title": title or "",
            "repo_url": repo_url or "",
            "path": path or "",
            "page_url": page_url or "",
            "content_sha256": content_hash or "",
            "frontmatter_name": original_name,
            "frontmatter_description": description,
            "body": body or "",
            "classification": result,
            "provenance": prov,
        }


def export(args):
    db = connect_readonly(args.db)
    wanted = {x.strip() for x in args.labels.split(",") if x.strip()}
    root = Path(args.out_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    selected = []
    used_names = defaultdict(set)
    for category_dir in root.iterdir():
        if category_dir.is_dir():
            used_names[category_dir.name].update(child.name for child in category_dir.iterdir() if child.is_dir())
    seen_content = set()

    for record in read_rows(db):
        stats["input_occurrences"] += 1
        label = record["classification"].get("label", "")
        if label not in wanted:
            stats["filtered_out_by_label"] += 1
            continue
        if args.only_with_content and not record["body"]:
            stats["without_content"] += 1
            continue
        content_key = record["content_sha256"] or f"{record['source']}:{record['external_id']}"
        if args.dedup_content and content_key in seen_content:
            stats["duplicate_occurrences_removed"] += 1
            continue
        seen_content.add(content_key)
        selected.append(record)

    manifest = {
        "manifest_version": "skill-folder-manifest-v2",
        "exporter_version": VERSION,
        "generated_at": utcnow(),
        "database": str(Path(args.db).expanduser().resolve()),
        "labels": sorted(wanted),
        "skill_filename": args.filename,
        "categories": [
            {"folder": item["folder"], "label": item["label"]}
            for item in PLOT_CATEGORY_BY_KEY.values()
        ],
        "records": [],
    }

    for index, record in enumerate(selected, 1):
        category_info, original_subtype = plot_category(record)
        category = category_info["folder"]
        category_dir = root / category
        category_dir.mkdir(parents=True, exist_ok=True)
        base_name = safe_folder_name(record["frontmatter_name"])
        folder_name = base_name
        if folder_name in used_names[category]:
            suffix_source = f"{record['source']}:{record['external_id']}".encode("utf-8")
            suffix = hashlib.sha1(suffix_source).hexdigest()[:8]
            folder_name = safe_folder_name(f"{base_name}__{suffix}")
            collision_number = 2
            while folder_name in used_names[category]:
                folder_name = safe_folder_name(f"{base_name}__{suffix}_{collision_number}")
                collision_number += 1
            stats["folder_name_collisions"] += 1
        used_names[category].add(folder_name)
        folder = category_dir / folder_name
        folder.mkdir(parents=True, exist_ok=False)
        skill_path = folder / args.filename
        skill_path.write_text(
            skill_markdown(record["frontmatter_name"], record["frontmatter_description"], record["body"]),
            encoding="utf-8",
            newline="\n",
        )
        stats["category_" + category] += 1
        if original_subtype not in SUBTYPE_TO_PLOT_CATEGORY:
            stats["unmapped_subtypes"] += 1
        stats["exported_records"] += 1
        manifest["records"].append({
            "category": category,
            "plot_category": category_info["label"],
            "folder": folder_name,
            "skill_file": f"{category}/{folder_name}/{args.filename}",
            "occurrence_id": record["occurrence_id"],
            "source": record["source"],
            "external_id": record["external_id"],
            "title": record["title"],
            "repo_url": record["repo_url"],
            "path": record["path"],
            "page_url": record["page_url"],
            "content_sha256": record["content_sha256"],
            "classification_label": record["classification"].get("label", ""),
            # Keep the fine-grained subtype for provenance without creating
            # subtype directories in the exported dataset.
            "classification_subtype": record["classification"].get("subtype", ""),
        })

    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    db.close()
    stats["output_dir"] = str(root)
    stats["manifest"] = str(root / "manifest.json")
    print(json.dumps({"exporter_version": VERSION, **stats}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Export database Skills as <name>/SKILL.md folders")
    parser.add_argument("--db", required=True, help="Crawler SQLite database")
    parser.add_argument("--out-dir", required=True, help="Outer directory for exported Skill folders")
    parser.add_argument("--labels", default="confirmed_direct", help="Comma-separated classifier labels; default confirmed_direct")
    parser.add_argument("--only-with-content", action=argparse.BooleanOptionalAction, default=True,
                        help="Skip records whose downloaded body is empty")
    parser.add_argument("--dedup-content", action=argparse.BooleanOptionalAction, default=True,
                        help="Export one folder per identical content hash")
    parser.add_argument("--filename", default=SKILL_FILENAME, choices=["SKILL.md", "skill.md"],
                        help="Skill file name; SKILL.md is the standard default")
    args = parser.parse_args()
    export(args)


if __name__ == "__main__":
    main()
