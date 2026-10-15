import tempfile,unittest
from scripts import skill_crawler as m
class Tests(unittest.TestCase):
 def test_skillsmp_infer(self):
  repo,slug=m.infer_page('https://skillsmp.com/creators/affaan-m/ecc/docs-zh-cn-skills-video-editing','skillsmp');self.assertEqual(repo,'https://github.com/affaan-m/ecc');self.assertEqual(slug,'docs-zh-cn-skills-video-editing')
 def test_flattened_path_match(self):
  score,reason=m.path_match_score('docs/zh-cn/skills/video-editing/SKILL.md','docs-zh-cn-skills-video-editing');self.assertGreaterEqual(score,80)
 def test_inferred_repo_not_overridden(self):
  selected,reason=m.choose_github_url(['https://github.com/wrong/footer','https://github.com/majiayu000/claude-skill-registry/tree/main/skills/data/ai-proofreading'],'https://github.com/majiayu000/claude-skill-registry','ai-proofreading');self.assertEqual(m.repo_key(selected[0]),'https://github.com/majiayu000/claude-skill-registry');self.assertEqual(reason,'matched_inferred_repo')
 def test_low_confidence_link_rejected(self):
  selected,reason=m.choose_github_url(['https://github.com/random/footer'],'','target-skill');self.assertIsNone(selected)
 def test_retry_unresolved(self):
  with tempfile.TemporaryDirectory() as d:
   path=d+'\\\\test.db';st=m.Store(path);c=m.Candidate('x','1');st.save(c,'');self.assertTrue(st.unresolved('x','1'));st.save(c,'---\nname: x\n---\nbody');self.assertFalse(st.unresolved('x','1'));st.db.close()
 def test_search_boundary(self):self.assertTrue(m.should_split_code_search(1000,1,2));self.assertEqual(m.CODE_SEARCH_MAX_PAGES,10)
if __name__=='__main__':unittest.main()



