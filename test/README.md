# TimeMachine Test Suite

This directory contains all tests and demos for the TimeMachine system.

## Test Files

### Core Functionality Tests
- **`test_basic_functionality.py`** - Tests core node wrapping and recording capabilities
- **`test_serialization.py`** - Tests state serialization for complex LangGraph objects  
- **`test_decorator_integration.py`** - Tests the `@timemachine.record()` decorator
- **`test_context_manager.py`** - Tests the `with timemachine.recording():` context manager

### Demo and Integration Tests  
- **`test_demo_sample_agent.py`** - Comprehensive demo showing all integration methods with sample agent functionality

### Test Runner
- **`run_all_tests.py`** - Runs all tests and provides summary results

## Running Tests

### Run All Tests
```bash
python test/run_all_tests.py
```

### Run Individual Tests
```bash
python test/test_basic_functionality.py
python test/test_serialization.py
python test/test_decorator_integration.py
python test/test_context_manager.py
python test/test_demo_sample_agent.py
```

## Test Databases

Tests create SQLite databases in the `test/` directory:
- `test_basic.db` - Basic functionality tests
- `test_decorator.db` - Decorator integration tests  
- `test_context.db` - Context manager tests
- `test_demo_*.db` - Demo approach databases

## What Gets Tested

### ✅ Core Recording
- Node execution recording
- State serialization/deserialization
- Error handling and recovery
- Database persistence

### ✅ Integration Methods
- `@timemachine.record()` decorator
- Direct `TimeMachineGraph` wrapping
- `with timemachine.recording():` context manager

### ✅ Complex Scenarios
- Multi-node graph execution
- LangChain message handling
- State flow between nodes
- Execution timing and status tracking

## Test Output

Tests use standardized prefixes:
- `[TEST]` - Test execution messages
- `[PASS]` - Success indicators  
- `[FAIL]` - Failure indicators
- `[INFO]` - Informational messages
- `[DEMO]` - Demo execution messages

## Requirements

All tests require:
- Python virtual environment activated (`.\venv\Scripts\activate`)
- Required dependencies from `requirements.txt`
- Project root in Python path (handled automatically by test files)
