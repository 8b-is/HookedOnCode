#!/usr/bin/env python3
"""
Debug version of the hook to see what's happening
"""
import json
import sys
import os

# Log to a file for debugging
debug_file = "/tmp/hook_debug.log"

def log(message):
    with open(debug_file, 'a') as f:
        f.write(f"{message}\n")

try:
    log("=== Hook started ===")

    # Read input from stdin
    input_data = json.load(sys.stdin)
    log(f"Input received: {json.dumps(input_data, indent=2)}")

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    log(f"Tool name: {tool_name}")
    log(f"Tool input: {json.dumps(tool_input, indent=2)}")

    # Check file path
    if tool_name == "Write":
        file_path = tool_input.get("filePath", "") or tool_input.get("file_path", "")
    elif tool_name in ["Edit", "MultiEdit"]:
        file_path = tool_input.get("filePath", "") or tool_input.get("file_path", "")
    else:
        file_path = ""

    log(f"File path extracted: {file_path}")

    # Check if it's a code file
    code_extensions = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb',
        '.go', '.rs', '.swift', '.kt', '.scala', '.clj', '.hs', '.ml',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.sql', '.html', '.css',
        '.scss', '.sass', '.less', '.vue', '.svelte', '.jsx', '.tsx'
    }

    if file_path:
        from pathlib import Path
        path = Path(file_path)
        is_code = path.suffix.lower() in code_extensions or path.name in {
            'Dockerfile', 'Makefile', 'CMakeLists.txt', 'package.json',
            'requirements.txt', 'Cargo.toml', 'go.mod', 'composer.json'
        }
        log(f"Is code file: {is_code}")
    else:
        log("No file path found")

    log("Hook completed")

except Exception as e:
    log(f"Error: {e}")
    import traceback
    log(traceback.format_exc())

# Exit silently to not block Claude
sys.exit(0)