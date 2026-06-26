# Agent Trace Validator

A lightweight Python library for validating JSON agent traces. It checks for:
- **Cycles**: Ensures no duplicate tool call IDs
- **Completeness**: Verifies every tool call has a matching response
- **Time Budget**: Confirms total elapsed time stays within limits

## Features

- Zero third-party dependencies (uses only Python standard library)
- Simple API with clear error messages
- Comprehensive test suite
- Easy to integrate into existing workflows

## Installation

Just copy `agent_trace_validator.py` into your project, or install via pip:

```bash
pip install agent-trace-validator  # Not yet available, copy the file instead
```

## Usage

### Basic Validation

```python
from agent_trace_validator import validate_trace, TraceValidationError

trace = {
    "steps": [
        {
            "timestamp": 100.0,
            "tool_call": {
                "id": "call_1",
                "name": "search",
                "arguments": {"query": "python tutorial"}
            }
        },
        {
            "timestamp": 101.5,
            "tool_response": {
                "id": "call_1",
                "output": "Found 10 results"
            }
        }
    ]
}

try:
    validate_trace(trace, time_budget_seconds=300.0)  # 5 minute budget
    print("Trace is valid!")
except TraceValidationError as e:
    print(f"Invalid trace: {e}")
```

### Loading from File

```python
from agent_trace_validator import load_trace_from_file, validate_trace

trace = load_trace_from_file("trace.json")
validate_trace(trace)
```

## Validation Rules

1. **No Cycles**: Each tool call ID must be unique
2. **Complete Responses**: Every `tool_call` must have a matching `tool_response` with the same ID
3. **Time Budget**: Elapsed time (max timestamp - min timestamp) must not exceed the budget

## Running Tests

```bash
# Run with unittest
python3 -m unittest discover

# Run with pytest
python3 -m pytest -q
```

## Example Error Cases

### Cycle Detection
```python
# This will raise TraceValidationError: Cycle detected
trace_with_cycle = {
    "steps": [
        {"tool_call": {"id": "duplicate_id"}},
        {"tool_call": {"id": "duplicate_id"}}  # Duplicate!
    ]
}
```

### Missing Response
```python
# This will raise TraceValidationError: Missing responses
trace_missing_response = {
    "steps": [
        {"tool_call": {"id": "call_1"}}  # No response for this call
    ]
}
```

### Time Budget Exceeded
```python
# This will raise TraceValidationError: Time budget exceeded
trace_long_duration = {
    "steps": [
        {"timestamp": 0, "tool_call": {"id": "call_1"}},
        {"timestamp": 600, "tool_response": {"id": "call_1"}}  # 10 minutes > 5 minute budget
    ]
}
```