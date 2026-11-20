import unittest
from resume_analyzer import extract_skills, compare_skills
from section_scorer import score_resume_sections
from database import initialize_database, get_analysis_history

class TestCore(unittest.TestCase):
    def test_skills(self):
        self.assertIn('langgraph', extract_skills('Python, LangGraph and RAG'))
        self.assertEqual(compare_skills(['python'], ['python', 'sql']), (['python'], ['sql'], 50))
    def test_sections(self):
        scores, total = score_resume_sections('PROFESSIONAL SUMMARY\nHello\nTECHNICAL SKILLS\nPython\nEDUCATION\nBTech')
        self.assertGreaterEqual(total, 0)
        self.assertIn('Education', scores)
    def test_database(self):
        initialize_database()
        self.assertIsInstance(get_analysis_history(), list)

if __name__ == '__main__':
    unittest.main()
