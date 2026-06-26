"""Demonstrate error cases for the Agent Trace Validator."""

from agent_trace_validator import validate_trace, TraceValidationError

print("=== Agent Trace Validator Error Demonstrations ===\n")

# Example 1: Cycle detection
print("1. Cycle Detection:")
trace_cycle = {
    "steps": [
        {
            "tool_call": {
                "id": "duplicate_id",
                "name": "search",
                "arguments": {"query": "python"}
            }
        },
        {
            "tool_call": {
                "id": "duplicate_id",  # Duplicate ID
                "name": "search",
                "arguments": {"query": "tutorial"}
            }
        }
    ]
}

try:
    validate_trace(trace_cycle)
    print("  ERROR: Should have detected cycle!")
except TraceValidationError as e:
    print(f"  ✓ Correctly detected: {e}")

# Example 2: Missing response
print("\n2. Missing Response:")
trace_missing = {
    "steps": [
        {
            "tool_call": {
                "id": "call_1",
                "name": "search",
                "arguments": {"query": "python"}
            }
        }
        # Missing response for call_1
    ]
}

try:
    validate_trace(trace_missing)
    print("  ERROR: Should have detected missing response!")
except TraceValidationError as e:
    print(f"  ✓ Correctly detected: {e}")

# Example 3: Time budget exceeded
print("\n3. Time Budget Exceeded:")
trace_time = {
    "steps": [
        {
            "timestamp": 0,
            "tool_call": {
                "id": "call_1",
                "name": "search",
                "arguments": {"query": "python"}
            }
        },
        {
            "timestamp": 600,  # 10 minutes
            "tool_response": {
                "id": "call_1",
                "output": "results"
            }
        }
    ]
}

try:
    validate_trace(trace_time, time_budget_seconds=300)  # 5 minute budget
    print("  ERROR: Should have detected time budget exceeded!")
except TraceValidationError as e:
    print(f"  ✓ Correctly detected: {e}")

print("\n=== All error demonstrations completed ===")