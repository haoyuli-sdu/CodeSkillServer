# CSS-993 Skill Collection

This directory contains the 993-skill corpus released with Code Skill Server.

Skills are grouped into seven publication-level categories. Every immediate child of a category directory is one skill package containing exactly one `SKILL.md` file. The checked-in `manifest.json` provides a deterministic inventory and SHA-256 digest for each file.

Run the repository-level validator after modifying the collection:

```bash
python verify_collection.py
```

The expected category counts are recorded in both the validator and the root README. A classification change must preserve the 993-skill total and update `manifest.json`.

## Rights and intended use

This directory contains third-party skill materials assembled as a research corpus. It is excluded from the repository's Apache-2.0 license and is provided for non-commercial research and educational use only. Copyright remains with the respective original authors or rights holders. Preserve existing attribution and comply with all applicable upstream terms. See [`../THIRD_PARTY_CONTENT.md`](../THIRD_PARTY_CONTENT.md) for the full notice.

