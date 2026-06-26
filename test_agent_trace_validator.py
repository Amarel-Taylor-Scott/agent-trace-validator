"""Tests for the Agent Trace Validator."""

import unittest
from agent_trace_validator import validate_trace, TraceValidationError


class TestAgentTraceValidator(unittest.TestCase):
    
    def test_valid_trace(self):
        """Test that a valid trace passes validation."""
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
        
        self.assertTrue(validate_trace(trace, time_budget_seconds=10.0))
    
    def test_cycle_detection(self):
        """Test that duplicate tool call IDs are detected as cycles."""
        trace = {
            "steps": [
                {
                    "timestamp": 100.0,
                    "tool_call": {
                        "id": "call_1",
                        "name": "search",
                        "arguments": {"query": "python"}
                    }
                },
                {
                    "timestamp": 101.0,
                    "tool_call": {
                        "id": "call_1",  # Duplicate ID
                        "name": "search",
                        "arguments": {"query": "tutorial"}
                    }
                }
            ]
        }
        
        with self.assertRaises(TraceValidationError) as context:
            validate_trace(trace)
        
        self.assertIn("Cycle detected", str(context.exception))
    
    def test_missing_tool_response(self):
        """Test that missing tool responses are detected."""
        trace = {
            "steps": [
                {
                    "timestamp": 100.0,
                    "tool_call": {
                        "id": "call_1",
                        "name": "search",
                        "arguments": {"query": "python tutorial"}
                    }
                }
                # Missing response for call_1
            ]
        }
        
        with self.assertRaises(TraceValidationError) as context:
            validate_trace(trace)
        
        self.assertIn("Missing responses", str(context.exception))
    
    def test_time_budget_exceeded(self):
        """Test that exceeding time budget is detected."""
        trace = {
            "steps": [
                {
                    "timestamp": 100.0,
                    "tool_call": {
                        "id": "call_1",
                        "name": "search",
                        "arguments": {"query": "python"}
                    }
                },
                {
                    "timestamp": 200.0,  # 100 seconds elapsed
                    "tool_response": {
                        "id": "call_1",
                        "output": "results"
                    }
                }
            ]
        }
        
        with self.assertRaises(TraceValidationError) as context:
            validate_trace(trace, time_budget_seconds=50.0)  # 50 second budget
        
        self.assertIn("Time budget exceeded", str(context.exception))
    
    def test_valid_trace_within_budget(self):
        """Test that a trace within time budget passes validation."""
        trace = {
            "steps": [
                {
                    "timestamp": 100.0,
                    "tool_call": {
                        "id": "call_1",
                        "name": "search",
                        "arguments": {"query": "python"}
                    }
                },
                {
                    "timestamp": 120.0,  # 20 seconds elapsed
                    "tool_response": {
                        "id": "call_1",
                        "output": "results"
                    }
                }
            ]
        }
        
        self.assertTrue(validate_trace(trace, time_budget_seconds=30.0))  # 30 second budget
    
    def test_empty_trace(self):
        """Test that an empty trace passes validation."""
        trace = {"steps": []}
        self.assertTrue(validate_trace(trace))
    
    def test_trace_without_steps(self):
        """Test that a trace without steps key passes validation."""
        trace = {}
        self.assertTrue(validate_trace(trace))
    
    def test_multiple_tool_calls_and_responses(self):
        """Test multiple tool calls with their responses."""
        trace = {
            "steps": [
                {
                    "timestamp": 100.0,
                    "tool_call": {
                        "id": "call_1",
                        "name": "search",
                        "arguments": {"query": "python"}
                    }
                },
                {
                    "timestamp": 101.0,
                    "tool_call": {
                        "id": "call_2",
                        "name": "fetch",
                        "arguments": {"url": "http://example.com"}
                    }
                },
                {
                    "timestamp": 102.0,
                    "tool_response": {
                        "id": "call_1",
                        "output": "search results"
                    }
                },
                {
                    "timestamp": 103.0,
                    "tool_response": {
                        "id": "call_2",
                        "output": "page content"
                    }
                }
            ]
        }
        
        self.assertTrue(validate_trace(trace))


if __name__ == '__main__':
    unittest.main()