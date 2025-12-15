"""Integration tests for document processing pipeline."""

import unittest
import sys
import os

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from pipeline_engine.adapters.persistence.memory import MemoryStateRepository
from document_processing.pipeline import create_document_pipeline
from document_processing.schemas import Document
from pipeline_engine.core.state import StepStatus


class TestDocumentProcessingIntegration(unittest.TestCase):
    """Integration tests for document processing pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = MemoryStateRepository()
        self.pipeline = create_document_pipeline(state_repository=self.repository)
    
    def test_full_document_processing(self):
        """Test complete document processing pipeline."""
        document = Document(
            id="test-doc-001",
            title="Test Document",
            content="Python is a programming language with dynamic semantics and high-level data structures."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        
        # Verify pipeline completed
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.COMPLETED)
        
        # Verify all steps completed
        self.assertTrue(inspector.is_step_completed("classify_text"))
        self.assertTrue(inspector.is_step_completed("extract_keywords"))
        self.assertTrue(inspector.is_step_completed("generate_report"))
        
        # Verify context has expected data
        context = self.pipeline.get_context()
        self.assertIsNotNone(context.get("category"))
        self.assertIsNotNone(context.get("keywords"))
        self.assertIsNotNone(context.get("report"))
    
    def test_classification_step_output(self):
        """Test classification step produces expected output."""
        document = Document(
            id="tech-doc",
            content="This document discusses algorithms and API design patterns."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        
        classification_output = inspector.get_step_output("classify_text")
        self.assertIsNotNone(classification_output)
        self.assertIn("category", classification_output)
        self.assertIn("confidence", classification_output)
        self.assertEqual(classification_output["category"], "technical")
    
    def test_keyword_extraction_step_output(self):
        """Test keyword extraction step produces expected output."""
        document = Document(
            id="test-doc",
            content="Python programming language provides excellent support for data structures and algorithms."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        
        keywords_output = inspector.get_step_output("extract_keywords")
        self.assertIsNotNone(keywords_output)
        self.assertIn("keywords", keywords_output)
        self.assertIsInstance(keywords_output["keywords"], list)
        self.assertGreater(len(keywords_output["keywords"]), 0)
    
    def test_report_generation_step(self):
        """Test report generation step creates final report."""
        document = Document(
            id="report-doc",
            title="Test Report",
            content="Business revenue and profit margins are important metrics."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        
        report_output = inspector.get_step_output("generate_report")
        self.assertIsNotNone(report_output)
        self.assertIn("report", report_output)
        
        report = report_output["report"]
        self.assertEqual(report.document_id, "report-doc")
        self.assertIsNotNone(report.category)
        self.assertIsInstance(report.keywords, list)
        self.assertIsNotNone(report.summary)
    
    def test_pipeline_state_persistence(self):
        """Test that pipeline state is persisted."""
        document = Document(
            id="persist-doc",
            content="Test content for persistence."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        pipeline_id = self.pipeline.pipeline_id
        
        # Verify state was saved
        self.assertTrue(self.repository.exists(pipeline_id))
        
        # Load and verify
        saved_state = self.repository.load(pipeline_id)
        self.assertEqual(saved_state.status, StepStatus.COMPLETED)
        self.assertEqual(len(saved_state.steps), 3)
    
    def test_step_dependencies_via_context(self):
        """Test that steps depend on previous step outputs via context."""
        document = Document(
            id="dependency-doc",
            content="Technical documentation about software architecture."
        )
        
        inspector = self.pipeline.run(initial_context={"document": document})
        
        # Extract keywords step should see classification output
        extract_input = inspector.get_step_input("extract_keywords")
        self.assertIn("category", extract_input)
        self.assertIn("classification", extract_input)
        
        # Generate report step should see both previous outputs
        report_input = inspector.get_step_input("generate_report")
        self.assertIn("category", report_input)
        self.assertIn("keywords", report_input)
    
    def test_different_document_categories(self):
        """Test pipeline handles different document categories."""
        test_cases = [
            ("technical", "Code functions and algorithms for API development"),
            ("business", "Revenue profit and market sales strategies"),
            ("legal", "Contract agreement and legal documentation"),
            ("general", "Random text about various topics")
        ]
        
        for expected_category, content in test_cases:
            with self.subTest(category=expected_category):
                document = Document(
                    id=f"doc-{expected_category}",
                    content=content
                )
                
                inspector = self.pipeline.run(initial_context={"document": document})
                classification_output = inspector.get_step_output("classify_text")
                
                self.assertEqual(classification_output["category"], expected_category)
                self.assertTrue(inspector.is_step_completed("generate_report"))


if __name__ == "__main__":
    unittest.main()

