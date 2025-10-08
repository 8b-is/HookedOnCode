#!/usr/bin/env python3
"""
Test script for the Ollama/LM Studio code suggestions hook.
This simulates the input that Claude Code would send to the hook.
"""

import json
import subprocess

def test_hook_with_sample_input():
    """Test the hook with sample input data."""

    # Sample input that simulates Claude Code writing a Python function
    sample_input = {
        "session_id": "test-session-123",
        "transcript_path": "/tmp/test-transcript.jsonl",
        "cwd": "/tmp",
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {
            "filePath": "/tmp/test_function.py",
            "content": """def calculate_fibonacci(n):
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

print(calculate_fibonacci(10))"""
        },
        "tool_response": {
            "filePath": "/tmp/test_function.py",
            "success": True
        }
    }

    # Create the test file
    with open("/tmp/test_function.py", "w") as f:
        f.write(sample_input["tool_input"]["content"])

    print("Testing hook with sample Python code...")
    print("Input code:")
    print(sample_input["tool_input"]["content"])
    print("\n" + "="*50 + "\n")

    try:
        # Run the hook script with the sample input
        result = subprocess.run([
            "python3", "/aidata/HookedOnCode/code_suggestions_hook.py"
        ],
        input=json.dumps(sample_input),
        text=True,
        capture_output=True,
        timeout=60
        )

        print("Hook exit code:", result.returncode)
        print("Hook stdout:")
        print(result.stdout)
        if result.stderr:
            print("Hook stderr:")
            print(result.stderr)

        # Try to parse JSON output if present
        if result.stdout.strip():
            try:
                output_data = json.loads(result.stdout)
                print("\nParsed JSON output:")
                print(json.dumps(output_data, indent=2))
            except json.JSONDecodeError:
                print("\nOutput is not valid JSON")

    except subprocess.TimeoutExpired:
        print("Hook timed out after 60 seconds")
    except Exception as e:
        print(f"Error running hook: {e}")

if __name__ == "__main__":
    test_hook_with_sample_input()