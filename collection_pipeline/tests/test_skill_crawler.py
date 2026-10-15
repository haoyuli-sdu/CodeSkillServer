import unittest
from scripts import skill_crawler as s

class Tests(unittest.TestCase):
    def test_sitemap(self):
        kind, urls = s.parse_sitemap(b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x/a</loc></url></urlset>')
        self.assertEqual(kind, 'urlset')
        self.assertEqual(urls, ['https://x/a'])

    def test_frontmatter(self):
        meta, body = s.parse_frontmatter('---\nname: demo\ndescription: "hello"\n---\n# Body')
        self.assertEqual(meta['name'], 'demo')
        self.assertIn('Body', body)

    def test_github(self):
        repo, path, ref = s.split_github('https://github.com/acme/repo/blob/main/skills/demo/SKILL.md')
        self.assertEqual(repo, 'https://github.com/acme/repo')
        self.assertEqual(path, 'skills/demo/SKILL.md')
        self.assertEqual(ref, 'main')

    def test_infer(self):
        repo, slug = s.infer_page('https://skills.sh/microsoft/azure-skills/python-appservice-deploy', 'skills_sh')
        self.assertEqual(repo, 'https://github.com/microsoft/azure-skills')
        self.assertEqual(slug, 'python-appservice-deploy')

    def test_html(self):
        x = s.html_meta('<title>Demo</title><meta name="description" content="A skill"><a href="https://github.com/acme/repo/tree/main/skills/demo">src</a>')
        self.assertEqual(x['title'], 'Demo')
        self.assertTrue(x['github_urls'])

    def test_codegen_classifier_relevant(self):
        result = s.classify_codegen_text('Python function implementation', 'Generate code and unit tests', '', 'Use algorithms and data structures.')
        self.assertEqual(result['label'], 'relevant')
        self.assertGreaterEqual(result['score'], 6)

    def test_codegen_classifier_negative(self):
        result = s.classify_codegen_text('AI video generation', 'Create marketing videos', '', '')
        self.assertEqual(result['label'], 'not_relevant')
    def test_non_ascii_github_url(self):
        url = s.iri_to_uri('https://api.github.com/repositories/1/contents/著作权权属、侵权纠纷/SKILL.md?ref=abc')
        self.assertIn('%E8%91%97', url)
        self.assertNotIn('著作权', url)
    def test_code_search_1000_boundary(self):
        self.assertTrue(s.should_split_code_search(1000, 1, 100))
        self.assertFalse(s.should_split_code_search(999, 1, 100))
        self.assertFalse(s.should_split_code_search(1000, 1, 1))
        self.assertEqual(s.CODE_SEARCH_MAX_PAGES, 10)
if __name__ == '__main__':
    unittest.main()



