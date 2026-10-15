import unittest
from scripts import direct_codegen_filter_v2 as f

class DirectFilterV2Tests(unittest.TestCase):
    def classify(self,title,description='',body='',content=True,provenance=None):
        return f.classify(title,description,'{}',body,content,provenance or [])

    def test_function_generation_confirmed(self):
        r=self.classify('Function implementer','Implement Python functions from specifications.')
        self.assertEqual(r['label'],'confirmed_direct')
        self.assertEqual(r['subtype'],'function_method_algorithm')

    def test_scaffold_app_without_code_word(self):
        r=self.classify('Next.js starter','Scaffold a production-ready web application.')
        self.assertIn(r['label'],{'confirmed_direct','probable_direct'})

    def test_openapi_client(self):
        r=self.classify('OpenAPI client','Generate a typed API client from a schema.')
        self.assertEqual(r['label'],'confirmed_direct')
        self.assertEqual(r['subtype'],'cli_sdk_client_plugin')

    def test_schema_to_models(self):
        r=self.classify('Model builder','Convert JSON schema to Pydantic models.')
        self.assertEqual(r['label'],'confirmed_direct')

    def test_figma_to_react(self):
        r=self.classify('UI implementer','Turn Figma designs into React code.')
        self.assertIn(r['label'],{'confirmed_direct','probable_direct'})

    def test_review_not_direct(self):
        r=self.classify('Reviewer','Review source code and explain quality problems.')
        self.assertEqual(r['label'],'not_direct')

    def test_best_practice_not_direct(self):
        r=self.classify('Python guide','Apply Python coding standards and best practices.')
        self.assertEqual(r['label'],'not_direct')

    def test_diagram_not_direct(self):
        r=self.classify('Diagrammer','Generate Mermaid diagrams from source code.')
        self.assertEqual(r['label'],'not_direct')

    def test_storyboard_not_code_generation(self):
        r=self.classify('分镜剧本写作','根据一句话生成类似电影格式的分镜剧本。')
        self.assertEqual(r['label'],'not_direct')

    def test_api_documentation_not_code_generation(self):
        r=self.classify('API docs','Generate complete API documentation from a repository.')
        self.assertEqual(r['label'],'not_direct')

    def test_xmind_test_document_not_code_generation(self):
        r=self.classify('Test case document','Generate an XMind test-case document from a PRD.')
        self.assertEqual(r['label'],'not_direct')
    def test_test_generation_direct(self):
        r=self.classify('Test writer','Generate unit tests and test fixtures for service methods.')
        self.assertEqual(r['label'],'confirmed_direct')
        self.assertEqual(r['subtype'],'test_code')

    def test_infra_generation_direct(self):
        r=self.classify('IaC','Generate Terraform code and Kubernetes manifests.')
        self.assertEqual(r['label'],'confirmed_direct')
        self.assertEqual(r['subtype'],'infra_config')

    def test_body_only_is_not_confirmed(self):
        r=self.classify('Developer workflow','General development workflow.','Use this Skill to generate functions and implement API endpoints.')
        self.assertNotEqual(r['label'],'confirmed_direct')

    def test_metadata_only_direct_is_probable(self):
        r=self.classify('Code generator','Generate source code from requirements.',content=False)
        self.assertEqual(r['label'],'probable_direct')

    def test_search_only_goes_to_review(self):
        prov=[{'query_text':'generate code','rank':1}]
        r=self.classify('Tool','Developer utility.',content=True,provenance=prov)
        self.assertEqual(r['label'],'manual_review')

if __name__=='__main__':
    unittest.main()

