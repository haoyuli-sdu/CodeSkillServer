# Code Skill Server

This repository contains the public research artifacts for **Code Skill Server: A Large-Scale Search Engine for Code Generation Skills**.

The release has two parts:

- `skill_collection/`: the curated corpus of **993 code-generation skills**, organized into seven categories.
- `collection_pipeline/`: the standard-library-only collection, filtering, auditing, and export pipeline used to build the corpus.

## Corpus overview

| Category | Skills |
| --- | ---: |
| Application Components | 116 |
| Code Migration | 40 |
| Data & Infrastructure | 144 |
| General & Functional Code | 290 |
| Testing | 117 |
| Tools, SDKs & Generators | 189 |
| Web & API | 97 |
| **Total** | **993** |

Each skill is stored as:

```text
skill_collection/<category>/<skill-name>/SKILL.md
```

`skill_collection/manifest.json` records the category, relative path, and SHA-256 digest of every released skill. The 993 entries are released skill packages; identical upstream content may occur in more than one package when it was collected as a distinct record.

## Validate the release

Python 3.10 or newer is recommended. The validation and collection pipeline use only the Python standard library.

```bash
python verify_collection.py
cd collection_pipeline
python -m unittest discover -s tests -p "test_*.py" -v
```

The first command checks all seven category counts, the 993-skill total, directory structure, UTF-8 readability, required frontmatter fields, and manifest hashes. The second command runs the collection-pipeline test suite.

## Build a collection

See [`collection_pipeline/README.md`](collection_pipeline/README.md) for the pipeline and [`collection_pipeline/LINUX_QUICKSTART.md`](collection_pipeline/LINUX_QUICKSTART.md) for a complete command-line example.

The crawler reads credentials from environment variables. Do not place API keys in source files or commit `.env` files.

## Citation

If you use this artifact, please cite the paper. A machine-readable author list is provided in [`CITATION.cff`](CITATION.cff).

## License

Original project code and documentation are licensed under the [Apache License 2.0](LICENSE). This includes the collection, filtering, auditing, export, validation, and continuous-integration code.

The 993 files under `skill_collection/` contain third-party skill materials and are **not** covered by Apache-2.0. They are provided for non-commercial research and educational use, subject to attribution, applicable upstream licenses, and other rights held by their original authors. See [THIRD_PARTY_CONTENT.md](THIRD_PARTY_CONTENT.md) before using or redistributing the corpus.

