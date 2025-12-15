"""Step to generate final report."""

from typing import Dict, Any, List
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context
from document_processing.schemas import Document, Report


class GenerateReportStep(Step):
    """Generates a final report from processed document data."""
    
    def __init__(self):
        super().__init__("generate_report")
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Generate final report from all processing steps."""
        document = context.get("document")
        category = context.get("category")
        keywords = context.get("keywords", [])
        
        if not document:
            raise ValueError("Document not found in context")
        
        if not isinstance(document, Document):
            raise ValueError("Invalid document type in context")
        
        if not category:
            raise ValueError("Category not found in context")
        
        summary = self._generate_summary(document, category, keywords)
        
        report = Report(
            document_id=document.id,
            category=category,
            keywords=keywords,
            summary=summary
        )
        
        return {
            "report": report,
            "summary": summary
        }
    
    def _generate_summary(self, document: Document, category: str, keywords: List[str]) -> str:
        """Generate a summary of the document processing."""
        keyword_str = ", ".join(keywords[:3])
        return f"Document '{document.id}' classified as '{category}' with key topics: {keyword_str}."

