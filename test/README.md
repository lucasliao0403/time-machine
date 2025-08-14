# TimeMachine Test Suite

This directory contains comprehensive tests for the TimeMachine system (Phase 1 & 2).

## Test Files

### Phase 1: Core Functionality Tests
- `test_basic_functionality.py` - Tests core node wrapping and recording
- `test_serialization.py` - Tests state serialization/deserialization
- `test_decorator_integration.py` - Tests @timemachine.record() decorator
- `test_context_manager.py` - Tests with timemachine.recording(): context manager
- `test_demo_sample_agent.py` - Integration test with sample agent

### Phase 2: Analysis & Replay Tests
- `test_phase2_llm_tracking.py` - Tests LLM call detection, cost analysis, and pattern detection
- `test_phase2_replay.py` - Tests replay engine and counterfactual analysis

### Test Runner
- `run_all_tests.py` - Runs all tests and provides summary

## Running Tests

### Run All Tests
```bash
python test/run_all_tests.py
```

### Run Individual Test Suites
```bash
# Phase 1 tests
python test/test_basic_functionality.py
python test/test_decorator_integration.py
python test/test_context_manager.py
python test/test_serialization.py
python test/test_demo_sample_agent.py

# Phase 2 tests
python test/test_phase2_llm_tracking.py
python test/test_phase2_replay.py
```

## Features Tested

### Phase 1: Core Recording
1. **Node Instrumentation**: Wrapping LangGraph nodes to record executions
2. **State Serialization**: Converting complex states to/from JSON
3. **Database Recording**: Storing executions in SQLite
4. **Integration Methods**: Decorator and context manager approaches
5. **Error Handling**: Graceful handling of errors during recording

### Phase 2: Analysis & Replay
1. **LLM Call Detection**: Identifying and tracking LLM calls within nodes
2. **Cost Analysis**: Calculating token usage and costs across models
3. **Pattern Detection**: Finding inefficiencies and optimization opportunities
4. **Replay Engine**: Re-executing recorded nodes with modifications
5. **Counterfactual Analysis**: "What if" scenarios with different parameters
6. **Response Caching**: Caching LLM responses for faster replays

## Test Results Interpretation

- **[PASS]** - Test passed successfully
- **[FAIL]** - Test failed, check error output
- **[INFO]** - Informational message
- **[WARNING]** - Warning message, test may have partial issues

## Test Database Files

Tests create temporary SQLite database files with names like:
- `test_*.db` - Temporary test databases
- `timemachine_cache.db` - Response cache test database

These are automatically cleaned up after test runs.