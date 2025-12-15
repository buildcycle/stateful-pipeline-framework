"""Document processing pipeline definition."""

from pipeline_engine.core.pipeline import Pipeline
from pipeline_engine.ports.state_repository import StateRepository
from document_processing.steps.classify_text import ClassifyTextStep
from document_processing.steps.extract_keywords import ExtractKeywordsStep
from document_processing.steps.generate_report import GenerateReportStep


def create_document_pipeline(state_repository: StateRepository = None) -> Pipeline:
    """
    Create a document processing pipeline.
    
    Args:
        state_repository: Optional state repository for persistence
        
    Returns:
        Configured Pipeline instance
    """
    steps = [
        ClassifyTextStep(),
        ExtractKeywordsStep(max_keywords=5),
        GenerateReportStep(),
    ]
    
    return Pipeline(steps=steps, state_repository=state_repository)

