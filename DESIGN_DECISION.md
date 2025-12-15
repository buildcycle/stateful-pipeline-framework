# Design Decisions

This document explains the design thinking, implementation approach, and architectural decisions behind the Pipeline Framework.

## Design Thinking: Project Structure

### Initial Thoughts

I wanted to build a **domain-agnostic pipeline framework** that could handle sequential, stateful data processing. The key requirements were:

- **Separation of Concerns**: Framework code must be completely separate from business logic
- **Extensibility**: Easy to add new steps and persistence mechanisms
- **Observability**: Full visibility into pipeline and step execution
- **Simplicity**: Minimal learning curve for developers

### Structure Design

I organized the project into three main areas:

**1. Framework Core (`src/pipeline_engine/`)**
- `core/`: Essential components (Pipeline, Step, Context, State, etc.)
- `ports/`: Abstract interfaces for dependency inversion
- `adapters/`: Concrete implementations (e.g., MemoryStateRepository)

**2. Example Usage (`document_processing/`)**
- Complete working example showing framework usage
- Demonstrates step dependencies via shared context
- No business logic leaks into framework

**3. Tests (`tests/`)**
- Unit tests for each framework component
- Integration tests for complete workflows
- Tests for example pipeline

This structure ensures the framework remains pure and reusable while providing clear usage examples.

## Implementation: Building the Structure

### Core Components

**Pipeline Orchestrator**
- Created `Pipeline` class to manage sequential step execution
- Implemented state tracking at both pipeline and step levels
- Added optional state persistence via repository pattern
- Built-in error handling with step-level error propagation

**Step Interface**
- Defined minimal `Step` abstract class with single `execute()` method
- Steps receive `Context` and return dictionary of outputs
- Simple interface allows maximum flexibility

**Context Management**
- Implemented mutable `Context` class for shared data
- Steps can read from and write to context
- Context automatically propagates between steps

**State Tracking**
- Created `PipelineState` and `StepState` dataclasses
- Track status, inputs, outputs, errors, and timestamps
- State can be persisted via `StateRepository` interface

**Inspection API**
- Built `PipelineInspector` for read-only state access
- Provides convenient methods to query step status, outputs, errors
- Enables debugging and monitoring without exposing internals

### Ports and Adapters Pattern

**Ports (`ports/state_repository.py`)**
- Defined `StateRepository` abstract interface
- Framework depends only on this abstraction
- Enables dependency inversion

**Adapters (`adapters/persistence/memory.py`)**
- Implemented `MemoryStateRepository` for in-memory storage
- Can be easily swapped with database, file system, or other implementations
- No framework changes needed for new persistence backends

### Error Handling

**Exception Hierarchy**
- `PipelineError`: Base exception
- `StepError`: Step-level failures with step name and original error
- `PipelineExecutionError`: Pipeline-level failures
- `RetryExhaustedError`: Retry mechanism exhaustion

**Error Propagation**
- Steps can raise any exception
- Framework catches and wraps in `StepError`
- Pipeline stops on first error, preserving state for inspection

### Retry Mechanism

**RetryConfig**
- Configurable max attempts, delay, and backoff multiplier
- Custom `retry_on` function to determine retry eligibility
- Exponential backoff for retry delays

**Retry Execution**
- Recursive retry function with attempt tracking
- Retries only when `retry_on` returns True
- Raises `RetryExhaustedError` when attempts exhausted

## Principles Application and Code Quality

### SOLID Principles

| Principle | Application | Implementation |
|-----------|-------------|----------------|
| **Single Responsibility** | Each class has one clear purpose | `Pipeline` orchestrates, `Context` manages data, `State` tracks execution, `Inspector` provides read-only access |
| **Open/Closed** | Open for extension, closed for modification | Custom `Step` implementations, pluggable `StateRepository` adapters, extensible `RetryConfig` |
| **Liskov Substitution** | Subtypes are interchangeable | Any `Step` or `StateRepository` implementation works with framework |
| **Interface Segregation** | Minimal, focused interfaces | `Step` has only `execute()`, `StateRepository` has save/load/exists |
| **Dependency Inversion** | Depend on abstractions | `Pipeline` uses `StateRepository` interface, not concrete classes |

### KISS (Keep It Simple, Stupid)

**Simple Interface**
- Single method interface: `execute(context) -> dict`
- No complex configuration or initialization required
- Straightforward API for common use cases

**Simple State Model**
- Clear enum: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
- Flat state structure, easy to understand
- No nested state machines

**Sequential Execution**
- One step after another, predictable order
- No parallel execution complexity
- Easy to reason about execution flow

### DRY (Don't Repeat Yourself)

**Shared Context**
- Single context object shared across all steps
- No manual data passing between steps
- Centralized data access pattern

**Reusable Components**
- `RetryConfig` reusable across different steps
- `StateRepository` interface allows multiple implementations
- Common error handling in framework, not in each step

**Framework Abstraction**
- State tracking, error handling, persistence handled by framework
- Steps focus only on business logic
- No boilerplate in step implementations

### WET (Write Everything Twice) - When Appropriate

**Step Implementations**
- Each step can have similar structure (get input, process, return output)
- Acceptable repetition because:
  - Steps are domain-specific, not framework code
  - Similar structure improves readability
  - Allows flexibility in step logic

**Example Pipeline**
- Document processing steps follow similar patterns
- Demonstrates usage clearly
- Makes examples easier to understand

### Code Quality Measures

**Type Hints**
- Used throughout for better IDE support and documentation
- Helps catch errors early

**Docstrings**
- Clear docstrings for all public classes and methods
- Explains purpose, parameters, and return values

**Error Messages**
- Descriptive error messages with context
- Includes step names and original errors

**Testing**
- Comprehensive unit tests for all components
- Integration tests for complete workflows
- 76 tests covering framework and example usage

## Tradeoffs

| Decision | Choice | Rationale | Impact |
|----------|--------|-----------|--------|
| **Simplicity vs. Features** | Simplicity | Sequential execution only, single context | Easier to understand, covers majority of use cases, can extend later |
| **Flexibility vs. Safety** | Flexibility | Mutable context, no type checking | Maximum flexibility for different domains, type checking can be added in steps |
| **Persistence vs. Performance** | Optional persistence | State persistence is optional | Can disable for performance-critical pipelines, add when needed |
| **Error Handling** | Fail-fast with inspection | Pipeline stops on first error, state preserved | Clear error semantics, easy debugging, retry mechanism provides recovery |
| **Dependencies** | No external dependencies | Uses only Python standard library | Easy to adopt, no dependency conflicts, lightweight |

## How Developers Can Use This Framework

### Basic Usage

**1. Define Your Steps**
```python
class MyStep(Step):
    def __init__(self):
        super().__init__("my_step")
    
    def execute(self, context: Context):
        input_data = context.get("input")
        result = process(input_data)
        return {"output": result}
```

**2. Create Pipeline**
```python
steps = [Step1(), Step2(), Step3()]
pipeline = Pipeline(steps)
```

**3. Run Pipeline**
```python
inspector = pipeline.run(initial_context={"input": "data"})
```

**4. Access Results**
```python
context = pipeline.get_context()
result = context.get("output")
```

### Advanced Usage

**With State Persistence**
```python
repository = MemoryStateRepository()
pipeline = Pipeline(steps, state_repository=repository)
inspector = pipeline.run()
```

**With Retry**
```python
retry_config = RetryConfig(
    max_attempts=5,
    delay=2.0,
    retry_on=lambda e: isinstance(e, NetworkError)
)
pipeline.retry_step("failed_step", retry_config)
```

**State Inspection**
```python
inspector = pipeline.get_inspector()
status = inspector.get_step_status("my_step")
output = inspector.get_step_output("my_step")
error = inspector.get_step_error("my_step")
```

### Extending the Framework

**Custom State Repository**
```python
class DatabaseStateRepository(StateRepository):
    def save(self, pipeline_id: str, state: PipelineState):
        # Your database persistence logic
    
    def load(self, pipeline_id: str) -> PipelineState:
        # Your database loading logic
    
    def exists(self, pipeline_id: str) -> bool:
        # Your existence check
```

**Custom Retry Logic**
```python
def should_retry_network_errors(error: Exception) -> bool:
    return isinstance(error, (ConnectionError, TimeoutError))

retry_config = RetryConfig(retry_on=should_retry_network_errors)
```

## Demo/Production Implementation

### What Was Implemented

**Framework Core**
- Complete pipeline orchestration engine
- Step interface and execution mechanism
- Context management and state tracking
- Error handling and retry mechanism
- State persistence abstraction
- Inspection API

**Example Pipeline (Document Processing)**
- Three-step pipeline: classify text, extract keywords, generate report
- Demonstrates step dependencies via shared context
- Shows how to structure domain-specific steps
- Runnable example with full output

**Testing Suite**
- 76 comprehensive tests
- Unit tests for all framework components
- Integration tests for complete workflows
- Tests for example pipeline

**Documentation**
- README with setup and usage instructions
- Design decisions document (this file)
- Code comments and docstrings

### Production Readiness

**Current State**
- Framework is functional and tested
- No external dependencies
- Clean separation of concerns
- Extensible architecture

**What's Missing for Production**
- Database adapters for state persistence
- Logging framework integration
- Metrics and monitoring hooks
- Performance optimization for large pipelines
- Security considerations (input validation, etc.)

## Scalability Considerations

### Current Limitations

- **Sequential Execution**: Steps run one at a time
- **In-Memory State**: Default repository is memory-based
- **Synchronous Only**: No async/await support
- **Single Context**: No branching or parallel execution

### Future Scalability Options

| Enhancement | Complexity | Benefit | Implementation Approach |
|-------------|------------|---------|------------------------|
| **Parallel Step Execution** | High | Performance for independent steps | Add step dependency graph, thread pool executor |
| **Distributed Execution** | Very High | Scale across machines | Message queue integration, distributed state repository |
| **Async/Await Support** | Medium | Better I/O performance | Rewrite execution loop with async, async step interface |
| **Database Adapters** | Low | Persistent state storage | Implement StateRepository for PostgreSQL, MongoDB, etc. |
| **Caching Layer** | Medium | Faster repeated executions | Add cache repository adapter, cache step outputs |
| **Step Dependencies (DAG)** | High | Complex workflows | Build dependency graph, topological sort execution |
| **Conditional Execution** | Medium | Branching logic | Add conditional step wrapper, context-based routing |
| **Web UI Dashboard** | Medium | Operational visibility | REST API for state access, web frontend |
| **Metrics & Monitoring** | Low | Production observability | Add metrics hooks, integrate with Prometheus/StatsD |
| **Pipeline Templates** | Low | Reusability | YAML/JSON pipeline definitions, template engine |

### Recommended Next Steps

**Short Term (Low Effort, High Value)**
1. Add database adapters (PostgreSQL, SQLite)
2. Integrate logging framework
3. Add metrics hooks

**Medium Term (Medium Effort, High Value)**
1. Implement async/await support
2. Add step dependency graph (DAG execution)
3. Build web UI dashboard

**Long Term (High Effort, High Value)**
1. Distributed execution support
2. Parallel step execution
3. Pipeline templates and configuration

The current architecture supports these enhancements without major refactoring, thanks to the ports/adapters pattern and clean separation of concerns.
