"""CLI runner for document processing pipeline (uses PyTorch models)."""

import sys
import os

# Add project root and src directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from pipeline_engine.adapters.persistence.memory import MemoryStateRepository
from document_processing.pipeline import create_document_pipeline
from document_processing.schemas import Document


def main():
    """Run the document processing pipeline example."""
    print("=" * 60)
    print("Document Processing Pipeline Example")
    print("=" * 60)
    
    state_repository = MemoryStateRepository()
    pipeline = create_document_pipeline(state_repository=state_repository)
    
    document = Document(
        id="doc-001",
        title="Python Programming Guide",
        content="Python is a high-level programming language with dynamic semantics. "
                "Its high-level built-in data structures, combined with dynamic typing "
                "and dynamic binding, make it very attractive for Rapid Application Development. "
                "Python supports multiple programming paradigms including object-oriented, "
                "imperative, functional, and procedural programming."
    )
    
    initial_context = {
        "document": document
    }
    
    print(f"\nProcessing document: {document.id}")
    print(f"Title: {document.title}")
    print(f"Content preview: {document.content[:100]}...")
    print("\n" + "-" * 60)
    print("Executing pipeline...")
    print("-" * 60)
    
    try:
        inspector = pipeline.run(initial_context=initial_context)
        
        print("\n[SUCCESS] Pipeline completed successfully!")
        print("\n" + "=" * 60)
        print("Pipeline Results")
        print("=" * 60)
        
        for step_name in ["classify_text", "extract_keywords", "generate_report"]:
            step_state = inspector.get_step_state(step_name)
            if step_state:
                print(f"\nStep: {step_name}")
                print(f"  Status: {step_state.status.value}")
                print(f"  Attempts: {step_state.attempts}")
                
                if step_state.output_data:
                    print(f"  Output keys: {list(step_state.output_data.keys())}")
        
        final_context = pipeline.get_context()
        report = final_context.get("report")
        
        if report:
            print("\n" + "=" * 60)
            print("Final Report")
            print("=" * 60)
            print(f"Document ID: {report.document_id}")
            print(f"Category: {report.category}")
            print(f"Keywords: {', '.join(report.keywords)}")
            print(f"Summary: {report.summary}")
        
        print("\n" + "=" * 60)
        print("State Inspection")
        print("=" * 60)
        
        keywords_output = inspector.get_step_output("extract_keywords")
        if keywords_output:
            print(f"\nKeywords extracted: {keywords_output.get('keywords', [])}")
        
        classification_output = inspector.get_step_output("classify_text")
        if classification_output:
            print(f"Category: {classification_output.get('category')}")
            print(f"Confidence: {classification_output.get('confidence')}")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        inspector = pipeline.get_inspector()
        
        print("\n" + "=" * 60)
        print("Error Details")
        print("=" * 60)
        
        for step_name in ["classify_text", "extract_keywords", "generate_report"]:
            if inspector.is_step_failed(step_name):
                error = inspector.get_step_error(step_name)
                print(f"\nFailed step: {step_name}")
                print(f"  Error: {error}")
        
        raise
    
    print("\n" + "=" * 60)
    print("Pipeline State Persistence")
    print("=" * 60)
    print(f"Pipeline ID: {pipeline.pipeline_id}")
    print(f"State saved: {state_repository.exists(pipeline.pipeline_id)}")
    
    if state_repository.exists(pipeline.pipeline_id):
        saved_state = state_repository.load(pipeline.pipeline_id)
        print(f"Saved status: {saved_state.status.value}")
        print(f"Total steps: {len(saved_state.steps)}")


if __name__ == "__main__":
    main()

