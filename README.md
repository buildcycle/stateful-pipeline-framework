# Pipeline Framework

A lightweight, extensible Python framework for building sequential, stateful data processing pipelines. Domain-agnostic and designed with clean architecture principles.

## Features

- **Sequential Execution**: Run steps in order with automatic state tracking
- **Shared Context**: Pass data between steps through a mutable context object
- **State Management**: Track inputs, outputs, status, and errors for every step
- **Error Handling**: Step-level error handling with propagation
- **Retry Mechanism**: Retry failed steps with exponential backoff
- **State Persistence**: Save and load pipeline state via repository abstraction
- **Inspection API**: Inspect pipeline and step states at any time

## Project Structure

```
Pipeline_Framework/
├── src/
│   └── pipeline_engine/          # Framework source code (dependency-free)
│       ├── core/                 # Core components
│       ├── ports/                # Interfaces
│       └── adapters/             # Implementations
├── document_processing/          # FastAPI + PyTorch application
│   ├── main.py                   # FastAPI application (entry point)
│   ├── pipeline.py               # Pipeline definition
│   ├── schemas.py                # Data models
│   ├── run_document_pipeline.py  # CLI runner
│   └── steps/                    # PyTorch-powered steps
│       ├── classify_text.py       # PyTorch classification
│       ├── extract_keywords.py    # PyTorch keyword extraction
│       └── generate_report.py    # Report generation
└── tests/                        # Test suite
    ├── unit/
    └── integration/
```

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- CUDA (optional, for GPU acceleration with PyTorch)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Pipeline_Framework
   ```

2. **Verify Python version:**
   ```bash
   python --version
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note:** The core framework can work without dependencies, but the example pipeline and API require:
   - FastAPI for REST API
   - PyTorch and Transformers for ML-powered document processing

## Running the Project

### Run the FastAPI Application (Recommended)

Start the FastAPI server with PyTorch-powered document processing:

```bash
python document_processing/main.py
```

Or using uvicorn directly:

```bash
uvicorn document_processing.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Note:** First run will download PyTorch models (~500MB). Models are cached for subsequent runs.

### Run the CLI Version

Execute the document processing example directly (without API):

```bash
python document_processing/run_document_pipeline.py
```

This will:
- Process a sample document using PyTorch models
- Classify the text with transformer models
- Extract keywords using NLP embeddings
- Generate a final report
- Display pipeline execution results

### Create Your Own Pipeline

1. **Import the framework:**
   ```python
   from pipeline_engine.core.pipeline import Pipeline
   from pipeline_engine.core.step import Step
   from pipeline_engine.core.context import Context
   ```

2. **Define your steps:**
   ```python
   class MyStep(Step):
       def __init__(self):
           super().__init__("my_step")
       
       def execute(self, context: Context):
           # Your logic here
           return {"output": "data"}
   ```

3. **Create and run the pipeline:**
   ```python
   steps = [MyStep()]
   pipeline = Pipeline(steps)
   inspector = pipeline.run(initial_context={"input": "value"})
   ```

See `document_processing/` for a complete example with PyTorch integration.

### Using the REST API

**Process a document:**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "doc-001",
    "title": "Python Guide",
    "content": "Python is a programming language with dynamic semantics."
  }'
```

**Get pipeline status:**
```bash
curl "http://localhost:8000/pipelines/{pipeline_id}"
```

**Get all step statuses:**
```bash
curl "http://localhost:8000/pipelines/{pipeline_id}/steps"
```

**Get specific step status:**
```bash
curl "http://localhost:8000/pipelines/{pipeline_id}/steps/{step_name}"
```

**Retry a failed step:**
```bash
curl -X POST "http://localhost:8000/pipelines/{pipeline_id}/retry/{step_name}"
```

**Health check:**
```bash
curl "http://localhost:8000/health"
```

## Testing

### Run All Tests

Execute the full test suite from the project root:

```bash
# Using pytest (recommended)
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests -v
```

**Note:** Make sure you're in the project root directory (`Pipeline_Framework/`) when running tests.

### Run Unit Tests Only

Test individual framework components:

```bash
python -m unittest tests.unit -v
```

Or run specific test files:

```bash
python -m unittest tests.unit.test_pipeline -v
python -m unittest tests.unit.test_context -v
python -m unittest tests.unit.test_retry -v
```

### Run Integration Tests Only

Test complete pipeline workflows:

```bash
python -m unittest tests.integration -v
```

### Test Coverage

Generate coverage report (requires `coverage` package):

```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generates HTML report
```

## Quick Start Example

```python
from pipeline_engine.core.pipeline import Pipeline
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context

class GreetStep(Step):
    def __init__(self):
        super().__init__("greet")
    
    def execute(self, context: Context):
        name = context.get("name", "World")
        return {"greeting": f"Hello, {name}!"}

# Create and run pipeline
pipeline = Pipeline([GreetStep()])
inspector = pipeline.run(initial_context={"name": "Pipeline"})

# Check results
print(pipeline.get_context().get("greeting"))
# Output: Hello, Pipeline!
```

## Key Concepts

- **Step**: A single unit of work that implements the `Step` interface
- **Context**: Shared mutable object passed between steps
- **Pipeline**: Orchestrates sequential step execution
- **State**: Tracks execution status, inputs, outputs, and errors
- **Inspector**: Provides read-only access to pipeline state
- **Repository**: Abstract interface for state persistence

## Technology Stack

- **Core Framework**: Pure Python (standard library only)
- **REST API**: FastAPI for web endpoints
- **Machine Learning**: PyTorch and Transformers for NLP tasks
- **Documentation**: Auto-generated API docs with Swagger/ReDoc

## Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Step-by-step guide with API examples and screenshots
- **[DESIGN_DECISION.md](DESIGN_DECISION.md)** - Architecture and design decisions
