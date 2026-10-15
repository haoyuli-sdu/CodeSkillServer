# Skill Collection Pipeline

This directory contains the collection and filtering pipeline used for the Code Skill Server corpus.

## Components

- `scripts/skill_crawler.py`: polite, provenance-first multi-source crawler.
- `scripts/targeted_codegen_crawler.py`: high-recall discovery and resolution for direct code-generation skills.
- `scripts/direct_codegen_filter_v2.py`: rule-based direct code-generation classifier.
- `scripts/merge_targeted_dbs.py`: merges per-source SQLite databases.
- `scripts/resolve_unresolved.py`: resolves metadata-only records to `SKILL.md` content.
- `scripts/audit_skill_dataset.py`: produces data-quality audit reports.
- `scripts/export_skills_as_folders.py`: exports classified records as folder-based skill packages.

The scripts use the Python standard library and do not execute downloaded skill code.

## Test

From this directory:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Run

See [`LINUX_QUICKSTART.md`](LINUX_QUICKSTART.md) for the end-to-end workflow. API credentials are read from environment variables such as `GITHUB_TOKEN`; never write credentials into the scripts or commit local environment files.

