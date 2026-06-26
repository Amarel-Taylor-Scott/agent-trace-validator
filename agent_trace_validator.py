"""Agent Trace Validator - Validate JSON agent traces for cycles, completeness, and time budgets."""

import json
import time
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict


class TraceValidationError(Exception):
    """Exception raised for trace validation errors."""
    pass


def validate_trace(trace: Dict[str, Any], time_budget_seconds: float = 300.0) -> bool:
    """
    Validate a JSON agent trace for cycles, completeness, and time budget.
    
    Args:
        trace: Dictionary representing the agent trace
        time_budget_seconds: Maximum allowed time in seconds (default: 300 = 5 minutes)
        
    Returns:
        True if trace is valid
        
    Raises:
        TraceValidationError: If validation fails
    """
    # Validate structure
    if not isinstance(trace, dict):
        raise TraceValidationError("Trace must be a dictionary")
    
    steps = trace.get("steps", [])
    if not isinstance(steps, list):
        raise TraceValidationError("Trace 'steps' must be a list")
    
    # Check for cycles
    _check_for_cycles(steps)
    
    # Check that all tool calls have outputs
    _check_tool_call_completeness(steps)
    
    # Check time budget
    _check_time_budget(steps, time_budget_seconds)
    
    return True


def _check_for_cycles(steps: List[Dict[str, Any]]) -> None:
    """Check for cycles in tool calls."""
    tool_call_ids = set()
    
    for step in steps:
        if "tool_call" in step:
            call_id = step["tool_call"].get("id")
            if call_id:
                if call_id in tool_call_ids:
                    raise TraceValidationError(f"Cycle detected: duplicate tool call ID '{call_id}'")
                tool_call_ids.add(call_id)


def _check_tool_call_completeness(steps: List[Dict[str, Any]]) -> None:
    """Check that every tool call has a corresponding output."""
    tool_call_ids = set()
    tool_response_ids = set()
    
    for step in steps:
        if "tool_call" in step:
            call_id = step["tool_call"].get("id")
            if call_id:
                tool_call_ids.add(call_id)
        elif "tool_response" in step:
            response_id = step["tool_response"].get("id")
            if response_id:
                tool_response_ids.add(response_id)
    
    # Check for missing responses
    missing_responses = tool_call_ids - tool_response_ids
    if missing_responses:
        raise TraceValidationError(f"Missing responses for tool calls: {missing_responses}")


def _check_time_budget(steps: List[Dict[str, Any]], time_budget_seconds: float) -> None:
    """Check that total elapsed time stays within budget."""
    if not steps:
        return
    
    # Find start and end times
    start_time = None
    end_time = None
    
    for step in steps:
        if "timestamp" in step:
            timestamp = step["timestamp"]
            if start_time is None or timestamp < start_time:
                start_time = timestamp
            if end_time is None or timestamp > end_time:
                end_time = timestamp
    
    if start_time is not None and end_time is not None:
        elapsed = end_time - start_time
        if elapsed > time_budget_seconds:
            raise TraceValidationError(
                f"Time budget exceeded: {elapsed:.2f}s > {time_budget_seconds:.2f}s"
            )


def load_trace_from_file(filepath: str) -> Dict[str, Any]:
    """Load a trace from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


# Example usage
if __name__ == "__main__":
    # Example trace
    example_trace = {
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
            },
            {
                "timestamp": 102.0,
                "tool_call": {
                    "id": "call_2",
                    "name": "fetch",
                    "arguments": {"url": "http://example.com"}
                }
            },
            {
                "timestamp": 103.2,
                "tool_response": {
                    "id": "call_2",
                    "output": "Page content"
                }
            }
        ]
    }
    
    try:
        validate_trace(example_trace, time_budget_seconds=10.0)
        print("Trace is valid!")
    except TraceValidationError as e:
        print(f"Validation error: {e}")