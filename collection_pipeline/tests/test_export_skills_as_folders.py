import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import export_skills_as_folders as exporter
from scripts import skill_crawler


class SkillFolderExportTests(unittest.TestCase):
    def test_classifier_subtypes_fold_into_seven_public_categories(self):
        self.assertEqual(len(exporter.PLOT_CATEGORY_ORDER), 7)
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "cli_sdk_client_plugin"}}),
            "01_Tools_SDKs_Generators",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "function_method_algorithm"}}),
            "02_General_Functional_Code",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "infra_config"}}),
            "03_Data_Infrastructure",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "test_code"}}),
            "04_Testing",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "full_app_scaffold"}}),
            "05_Application_Components",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "backend_api"}}),
            "06_Web_API",
        )
        self.assertEqual(
            exporter.category_folder({"classification": {"subtype": "code_conversion_migration"}}),
            "07_Code_Migration",
        )

    def test_exports_standard_skill_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "skills.db"
            store = skill_crawler.Store(str(db))
            c = skill_crawler.Candidate("github", "x", "https://example/x", "demo", "", "https://github.com/acme/demo", "skills/demo/SKILL.md", "", "demo", {})
            md = "---\nname: demo\ndescription: Generate functions.\n---\n\n# Demo\n\nImplement functions from specs."
            store.save(c, md)
            store.db.close()
            out = Path(directory) / "exported"
            exporter.export(SimpleNamespace(db=str(db), out_dir=str(out), labels="confirmed_direct", only_with_content=True, dedup_content=True, filename="SKILL.md"))
            skill_file = out / "02_General_Functional_Code" / "demo" / "SKILL.md"
            self.assertTrue(skill_file.exists())
            self.assertIn('name: "demo"', skill_file.read_text(encoding="utf-8"))
            self.assertIn("Implement functions", skill_file.read_text(encoding="utf-8"))
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["records"]), 1)
            self.assertEqual(manifest["records"][0]["skill_file"], "02_General_Functional_Code/demo/SKILL.md")
            self.assertEqual(manifest["records"][0]["plot_category"], "General & Functional Code")

    def test_collision_gets_safe_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "skills.db"
            store = skill_crawler.Store(str(db))
            for eid, repo in [("a", "https://github.com/a/x"), ("b", "https://github.com/b/x")]:
                c = skill_crawler.Candidate("github", eid, "", "Same", "", repo, "SKILL.md", "", "same", {})
                store.save(c, f"---\nname: same\ndescription: Generate code {eid}.\n---\nBody {eid}")
            store.db.close()
            out = Path(directory) / "exported"
            exporter.export(SimpleNamespace(db=str(db), out_dir=str(out), labels="confirmed_direct", only_with_content=True, dedup_content=True, filename="SKILL.md"))
            folders = [x.name for x in (out / "02_General_Functional_Code").iterdir() if x.is_dir()]
            self.assertEqual(len(folders), 2)
            self.assertTrue(any(name.startswith("same__") for name in folders))

    def test_lowercase_filename_option(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "skills.db"
            store = skill_crawler.Store(str(db))
            c = skill_crawler.Candidate("github", "x", "", "demo", "", "", "", "", "demo", {})
            store.save(c, "---\nname: demo\ndescription: Generate code.\n---\nBody")
            store.db.close()
            out = Path(directory) / "exported"
            exporter.export(SimpleNamespace(db=str(db), out_dir=str(out), labels="confirmed_direct", only_with_content=True, dedup_content=True, filename="skill.md"))
            self.assertTrue((out / "02_General_Functional_Code" / "demo" / "skill.md").exists())


if __name__ == "__main__":
    unittest.main()


