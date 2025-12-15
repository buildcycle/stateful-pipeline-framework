"""FastAPI application for Document Processing Pipeline."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from pipeline_engine.core.pipeline import Pipeline
from pipeline_engine.adapters.persistence.memory import MemoryStateRepository
from document_processing.pipeline import create_document_pipeline
from document_processing.schemas import Document

app = FastAPI(
    title="Document Processing Pipeline",
    description="PyTorch-powered document processing pipeline with FastAPI",
    version="1.0.0"
)

# In-memory storage for pipelines
pipeline_storage: Dict[str, Pipeline] = {}
state_repository = MemoryStateRepository()


class DocumentRequest(BaseModel):
    """Request model for document processing."""
    id: str
    content: str
    title: Optional[str] = None


class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""
    pipeline_id: str
    status: str
    steps: Dict[str, Any]
    context: Dict[str, Any]
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StepStatusResponse(BaseModel):
    """Response model for step status."""
    step_name: str
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Document Processing Pipeline API",
        "version": "1.0.0",
        "framework": "FastAPI + PyTorch",
        "endpoints": {
            "POST /process": "Process a document through the pipeline",
            "GET /pipelines/{pipeline_id}": "Get pipeline status",
            "GET /pipelines/{pipeline_id}/steps": "Get all step statuses",
            "GET /pipelines/{pipeline_id}/steps/{step_name}": "Get specific step status",
            "POST /pipelines/{pipeline_id}/retry/{step_name}": "Retry a failed step",
            "GET /health": "Health check"
        }
    }


@app.post("/process", response_model=PipelineResponse)
async def process_document(document: DocumentRequest):
    """
    Process a document through the PyTorch-powered pipeline.
    
    The pipeline will:
    1. Classify the document text using PyTorch transformer models
    2. Extract keywords using NLP embeddings
    3. Generate a comprehensive report
    
    - **id**: Document identifier
    - **content**: Document text content (will be processed with PyTorch models)
    - **title**: Optional document title
    """
    try:
        # Create document object
        doc = Document(
            id=document.id,
            content=document.content,
            title=document.title
        )
        
        # Create and run pipeline
        pipeline = create_document_pipeline(state_repository=state_repository)
        pipeline_storage[pipeline.pipeline_id] = pipeline
        
        initial_context = {"document": doc}
        inspector = pipeline.run(initial_context=initial_context)
        
        # Get step statuses
        steps_status = {}
        for step_name in ["classify_text", "extract_keywords", "generate_report"]:
            step_state = inspector.get_step_state(step_name)
            if step_state:
                steps_status[step_name] = {
                    "status": step_state.status.value,
                    "attempts": step_state.attempts,
                    "has_output": step_state.output_data is not None,
                    "has_error": step_state.error is not None
                }
        
        # Get final report
        context = pipeline.get_context()
        report = context.get("report")
        report_dict = None
        if report:
            report_dict = {
                "document_id": report.document_id,
                "category": report.category,
                "keywords": report.keywords,
                "summary": report.summary
            }
        
        return PipelineResponse(
            pipeline_id=pipeline.pipeline_id,
            status=inspector.get_pipeline_status().value,
            steps=steps_status,
            context=context.to_dict(),
            report=report_dict,
            error=inspector.get_pipeline_error()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline_status(pipeline_id: str):
    """Get the status of a pipeline by ID."""
    if pipeline_id not in pipeline_storage:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipeline_storage[pipeline_id]
    inspector = pipeline.get_inspector()
    
    steps_status = {}
    for step_name, step_state in inspector.get_all_steps().items():
        steps_status[step_name] = {
            "status": step_state.status.value,
            "attempts": step_state.attempts,
            "has_output": step_state.output_data is not None,
            "has_error": step_state.error is not None
        }
    
    context = pipeline.get_context()
    report = context.get("report")
    report_dict = None
    if report:
        report_dict = {
            "document_id": report.document_id,
            "category": report.category,
            "keywords": report.keywords,
            "summary": report.summary
        }
    
    return PipelineResponse(
        pipeline_id=pipeline_id,
        status=inspector.get_pipeline_status().value,
        steps=steps_status,
        context=context.to_dict(),
        report=report_dict,
        error=inspector.get_pipeline_error()
    )


@app.get("/pipelines/{pipeline_id}/steps", response_model=Dict[str, StepStatusResponse])
async def get_all_step_statuses(pipeline_id: str):
    """Get status of all steps in a pipeline."""
    if pipeline_id not in pipeline_storage:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipeline_storage[pipeline_id]
    inspector = pipeline.get_inspector()
    
    steps = {}
    for step_name, step_state in inspector.get_all_steps().items():
        steps[step_name] = StepStatusResponse(
            step_name=step_state.step_name,
            status=step_state.status.value,
            input_data=step_state.input_data,
            output_data=step_state.output_data,
            error=step_state.error,
            attempts=step_state.attempts
        )
    
    return steps


@app.get("/pipelines/{pipeline_id}/steps/{step_name}", response_model=StepStatusResponse)
async def get_step_status(pipeline_id: str, step_name: str):
    """Get status of a specific step."""
    if pipeline_id not in pipeline_storage:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipeline_storage[pipeline_id]
    inspector = pipeline.get_inspector()
    
    step_state = inspector.get_step_state(step_name)
    if not step_state:
        raise HTTPException(status_code=404, detail=f"Step '{step_name}' not found")
    
    return StepStatusResponse(
        step_name=step_state.step_name,
        status=step_state.status.value,
        input_data=step_state.input_data,
        output_data=step_state.output_data,
        error=step_state.error,
        attempts=step_state.attempts
    )


@app.post("/pipelines/{pipeline_id}/retry/{step_name}")
async def retry_step(pipeline_id: str, step_name: str):
    """Retry a failed step in a pipeline."""
    if pipeline_id not in pipeline_storage:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipeline_storage[pipeline_id]
    
    try:
        from pipeline_engine.core.retry import RetryConfig
        retry_config = RetryConfig(max_attempts=3, delay=1.0)
        pipeline.retry_step(step_name, retry_config)
        
        inspector = pipeline.get_inspector()
        step_state = inspector.get_step_state(step_name)
        
        return {
            "message": f"Step '{step_name}' retried successfully",
            "status": step_state.status.value,
            "attempts": step_state.attempts
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "document-processing-pipeline",
        "framework": "FastAPI",
        "ml_framework": "PyTorch"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

