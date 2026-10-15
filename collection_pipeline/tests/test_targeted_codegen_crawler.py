import json
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from scripts import targeted_codegen_crawler as t

class TargetedCrawlerTests(unittest.TestCase):
    def test_profile_is_large_and_unique(self):
        profile, queries = t.load_profile(t.PROFILE_DEFAULT, 'core,extended', '', 0)
        self.assertGreaterEqual(len(queries), 250)
        self.assertEqual(len(queries), len({q['text'].casefold() for q in queries}))
        self.assertIn('code generation', {q['text'] for q in queries})
        self.assertIn('生成代码', {q['text'] for q in queries})

    def test_gate_explicit_direct(self):
        r = t.metadata_gate('OpenAPI SDK generator', 'Generate a typed API client from an OpenAPI schema.', {'tags':['typescript','sdk']}, ['generate API client'], 2)
        self.assertEqual(r['label'], 'auto_resolve')
        self.assertGreaterEqual(r['score'], 9)

    def test_gate_scaffold_without_word_code(self):
        r = t.metadata_gate('Next starter', 'Scaffold a production-ready Next.js application.', {'category':'frontend'}, ['scaffold application'], 5)
        self.assertEqual(r['label'], 'auto_resolve')

    def test_gate_review_is_not_auto_direct(self):
        r = t.metadata_gate('Code reviewer', 'Review code and explain quality problems.', {'tags':['review']}, ['code generation'], 80)
        self.assertNotEqual(r['label'], 'auto_resolve')

    def test_gate_media_rejected(self):
        r = t.metadata_gate('Image generator', 'Generate marketing images and social posts.', {}, ['code generation'], 70)
        self.assertEqual(r['label'], 'metadata_rejected')

    def test_flexible_item_normalization(self):
        item={'id':'x','name':'SDK maker','description':'Generate an API client','repository':{'url':'https://github.com/acme/sdk'},'tags':['codegen']}
        c=t.candidate_from_item('smithery',item,1,'q:1','generate SDK')
        self.assertEqual(c.repo_url,'https://github.com/acme/sdk')
        self.assertEqual(c.external_id,'x')

    def test_skillsmp_uses_bearer_auth(self):
        with patch.dict(t.os.environ, {'SKILLSMP_API_KEY':'secret'}, clear=False):
            self.assertEqual(t.auth_headers('skillsmp'), {'Authorization':'Bearer secret'})

    def test_skillsmp_page_size_is_50(self):
        url=t.source_url('skillsmp','generate code',100,page=2)
        self.assertIn('limit=50',url)
        self.assertIn('page=2',url)

    def test_skillsmp_paginates_per_query(self):
        calls=[]
        def fake_api(http,url,headers):
            calls.append(url)
            page=2 if 'page=2' in url else 1
            start=50 if page==2 else 0
            size=10 if page==2 else 50
            return {'skills':[{'id':f's{start+i}','name':f'Skill {start+i}','description':'Generate source code'} for i in range(size)]},{}
        q={'id':'g:1','text':'generate code','group':'g','tier':'core'}
        with patch.object(t,'api_get_json',side_effect=fake_api):
            rows=list(t.discover_json_source(object(),'skillsmp',q,60))
        self.assertEqual(len(rows),60)
        self.assertEqual(len(calls),2)
    def test_claude_plugins_uses_skill_endpoint(self):
        self.assertEqual(t.SOURCE_SPECS['claude_plugins']['endpoint'], 'https://claude-plugins.dev/api/skills')
        url=t.source_url('claude_plugins','generate code',30)
        self.assertIn('/api/skills?',url)
        self.assertIn('offset=0',url)
        self.assertNotIn('sort=',url)
    def test_github_long_query_uses_broad_anchors(self):
        expression=t.github_query_expression('implement functions from detailed specifications')
        self.assertIn('implement',expression)
        self.assertIn('function',expression)
        self.assertNotIn('"implement functions from detailed specifications"',expression)
    def test_queries_per_group_pilot(self):
        _, queries = t.load_profile(t.PROFILE_DEFAULT, 'core', '', 0, 3)
        groups = {q['group'] for q in queries}
        self.assertGreaterEqual(len(groups), 10)
        self.assertLessEqual(len(queries), len(groups) * 3)

    def test_list_items_nested_payload(self):
        payload={'data':{'results':[{'id':'a'},{'id':'b'}]}}
        self.assertEqual(len(t.list_items(payload)),2)
    def test_targeted_tables_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'x.db'); store=t.TargetedStore(db)
            q={'id':'g:001','text':'generate code','group':'g','tier':'core'}
            run=store.start_search('github',q,'p1',10);store.finish_search(run,0,0,'')
            self.assertTrue(store.search_completed('github','g:001','p1',10))
            self.assertFalse(store.search_completed('github','g:001','p1',20))
            store.db.close()

if __name__=='__main__':
    unittest.main()








