#!/usr/bin/env python3
"""
Test suite for code_suggestions_hook.py
Tests the Claude Code Hook for code suggestions using Ollama or LM Studio
"""

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

# Colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{BLUE}{BOLD}═══ {test_name} ═══{RESET}")

def print_result(success, message):
    """Print test result with color"""
    if success:
        print(f"{GREEN}✓ {message}{RESET}")
    else:
        print(f"{RED}✗ {message}{RESET}")

def run_hook(input_data):
    """Run the hook with given input and return the result"""
    try:
        # Run the hook script
        result = subprocess.run(
            ['python3', 'code_suggestions_hook.py'],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=35  # Give enough time for LLM to respond
        )

        # Check if there's output
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}

        # If no output and no error, hook passed through
        if result.returncode == 0:
            return {"status": "passthrough"}

        # If there was an error
        if result.stderr:
            return {"error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"error": "Hook timed out"}
    except Exception as e:
        return {"error": str(e)}

def test_write_python_file():
    """Test Write tool with Python file"""
    print_test_header("Test 1: Write Python File")

    test_input = {
        "tool_name": "Write",
        "tool_input": {
            "filePath": "/tmp/test_script.py",
            "content": """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum is: {result}")"""
        },
        "tool_response": {"success": True}
    }

    result = run_hook(test_input)

    if "decision" in result and result["decision"] == "block":
        print_result(True, "Hook triggered code analysis")
        print(f"{YELLOW}Suggestions received:{RESET}")
        print(result.get("reason", "No reason provided")[:500])  # Show first 500 chars
    elif result.get("status") == "passthrough":
        print_result(False, "Hook did not trigger (should analyze Python files)")
    else:
        print_result(False, f"Unexpected response: {result}")

def test_non_code_file():
    """Test with non-code file (should be ignored)"""
    print_test_header("Test 2: Non-Code File (README.md)")

    test_input = {
        "tool_name": "Write",
        "tool_input": {
            "filePath": "/tmp/README.md",
            "content": "# My Project\n\nThis is a README file."
        },
        "tool_response": {"success": True}
    }

    result = run_hook(test_input)

    if result.get("status") == "passthrough":
        print_result(True, "Correctly ignored non-code file")
    elif "decision" in result:
        print_result(False, "Hook incorrectly analyzed non-code file")
    else:
        print_result(False, f"Unexpected response: {result}")

def test_edit_javascript_file():
    """Test Edit tool with JavaScript file"""
    print_test_header("Test 3: Edit JavaScript File")

    # First create a temporary JavaScript file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("""function fetchData(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.log(error));
}

fetchData('https://api.example.com/data');""")
        temp_file = f.name

    test_input = {
        "tool_name": "Edit",
        "tool_input": {
            "filePath": temp_file,
            "old_string": "console.log(data)",
            "new_string": "console.log('Data:', data)"
        },
        "tool_response": {"success": True}
    }

    result = run_hook(test_input)

    # Clean up
    os.unlink(temp_file)

    if "decision" in result and result["decision"] == "block":
        print_result(True, "Hook triggered code analysis for JavaScript")
        print(f"{YELLOW}Suggestions received:{RESET}")
        print(result.get("reason", "No reason provided")[:500])
    elif result.get("status") == "passthrough":
        print_result(False, "Hook did not trigger for JavaScript file")
    else:
        print_result(False, f"Unexpected response: {result}")

def test_non_code_tool():
    """Test with non-code tool (should be ignored)"""
    print_test_header("Test 4: Non-Code Tool (Read)")

    test_input = {
        "tool_name": "Read",
        "tool_input": {
            "filePath": "/tmp/test.py"
        },
        "tool_response": {"content": "print('hello')"}
    }

    result = run_hook(test_input)

    if result.get("status") == "passthrough":
        print_result(True, "Correctly ignored non-code tool")
    elif "decision" in result:
        print_result(False, "Hook incorrectly processed non-code tool")
    else:
        print_result(False, f"Unexpected response: {result}")

def test_dockerfile():
    """Test with Dockerfile (special file without extension)"""
    print_test_header("Test 5: Dockerfile")

    test_input = {
        "tool_name": "Write",
        "tool_input": {
            "filePath": "/tmp/Dockerfile",
            "content": """FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]"""
        },
        "tool_response": {"success": True}
    }

    result = run_hook(test_input)

    if "decision" in result and result["decision"] == "block":
        print_result(True, "Hook correctly analyzed Dockerfile")
        print(f"{YELLOW}Suggestions received:{RESET}")
        print(result.get("reason", "No reason provided")[:500])
    elif result.get("status") == "passthrough":
        print_result(False, "Hook did not recognize Dockerfile")
    else:
        print_result(False, f"Unexpected response: {result}")

def check_llm_connectivity():
    """Check if LM Studio or Ollama is accessible"""
    print_test_header("Checking LLM Connectivity")

    # Read configuration from the hook
    use_lm_studio = True  # Matching the hook's configuration

    if use_lm_studio:
        host = "http://172.30.50.42:1234"
        print(f"Testing LM Studio connection at {host}")

        # Test LM Studio endpoint
        try:
            result = subprocess.run(
                ['curl', '-s', f'{host}/v1/models'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_result(True, f"LM Studio is accessible at {host}")
                try:
                    models = json.loads(result.stdout)
                    if 'data' in models and models['data']:
                        print(f"{GREEN}Available models:{RESET}")
                        for model in models['data'][:3]:  # Show first 3 models
                            print(f"  - {model.get('id', 'unknown')}")
                except:
                    pass
                return True
            else:
                print_result(False, f"LM Studio not accessible at {host}")
                return False
        except:
            print_result(False, f"Could not connect to LM Studio at {host}")
            return False
    else:
        host = "http://localhost:11434"
        print(f"Testing Ollama connection at {host}")

        # Test Ollama endpoint
        try:
            result = subprocess.run(
                ['curl', '-s', f'{host}/api/tags'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_result(True, f"Ollama is accessible at {host}")
                return True
            else:
                print_result(False, f"Ollama not accessible at {host}")
                return False
        except:
            print_result(False, f"Could not connect to Ollama at {host}")
            return False

def main():
    """Run all tests"""
    print(f"{BOLD}{BLUE}═══════════════════════════════════════")
    print(f"   Code Suggestions Hook Test Suite")
    print(f"═══════════════════════════════════════{RESET}")

    # First check LLM connectivity
    llm_available = check_llm_connectivity()

    if not llm_available:
        print(f"\n{YELLOW}⚠ Warning: LLM service not available{RESET}")
        print("The hook will not provide suggestions without an LLM service.")
        print("\nTo fix this:")
        print("1. For LM Studio: Start LM Studio and load a model")
        print("2. For Ollama: Run 'ollama serve' and 'ollama pull codellama'")
        print("\nContinuing with tests anyway...\n")

    # Run tests
    test_write_python_file()
    test_non_code_file()
    test_edit_javascript_file()
    test_non_code_tool()
    test_dockerfile()

    print(f"\n{BOLD}{BLUE}═══════════════════════════════════════{RESET}")
    print(f"{GREEN}Tests completed!{RESET}")

    if not llm_available:
        print(f"{YELLOW}Note: Some tests may have failed due to LLM unavailability{RESET}")

if __name__ == "__main__":
    main()