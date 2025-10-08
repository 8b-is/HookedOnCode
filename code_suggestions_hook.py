#!/usr/bin/env python3
"""
Claude Code Hook: Code Suggestions using Ollama or LM Studio

This hook runs after code-writing tools (Write, Edit, MultiEdit) and uses
a local LLM instance (Ollama or LM Studio) to provide code suggestions and improvements.
"""

import json
import sys
import subprocess
import os
from pathlib import Path

# Configuration
USE_SERVICE = os.getenv("CODE_HOOK_SERVICE", "openrouter")  # Options: "openrouter", "lm_studio", "ollama"

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Required for OpenRouter
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "x-ai/grok-code-fast-1")  # Grok Code Fast 1
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# LM Studio Configuration
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "nousresearch/hermes-4-70b")
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234")

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:7b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def is_code_file(file_path):
    """Check if the file contains code that should be analyzed."""
    code_extensions = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb',
        '.go', '.rs', '.swift', '.kt', '.scala', '.clj', '.hs', '.ml',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.sql', '.html', '.css',
        '.scss', '.sass', '.less', '.vue', '.svelte', '.jsx', '.tsx'
    }

    if not file_path:
        return False

    path = Path(file_path)
    return path.suffix.lower() in code_extensions or path.name in {
        'Dockerfile', 'Makefile', 'CMakeLists.txt', 'package.json',
        'requirements.txt', 'Cargo.toml', 'go.mod', 'composer.json'
    }

def get_code_content(tool_name, tool_input, tool_response):
    """Extract the code content from the tool input/response."""
    content = ""

    # For Write tool
    if tool_name == "Write":
        content = tool_input.get("content", "")

    # For Edit/MultiEdit tools, we need to read the file to see what changed
    elif tool_name in ["Edit", "MultiEdit"]:
        file_path = tool_input.get("filePath", "")
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                return ""

    return content.strip()

def get_ollama_suggestions(code_content, file_path):
    """Get code suggestions from Ollama."""
    if not code_content:
        return None

    # Create a prompt for code suggestions
    file_name = os.path.basename(file_path) if file_path else "code"
    prompt = f"""Analyze this code and provide suggestions for improvements:

File: {file_name}
```code
{code_content}
```

Please provide specific, actionable suggestions for:
1. Code quality improvements
2. Best practices
3. Potential bugs or issues
4. Performance optimizations
5. Security considerations

Keep suggestions concise and focused on the most important issues."""

    try:
        # Call Ollama API
        result = subprocess.run([
            'curl', '-s', f'{OLLAMA_HOST}/api/generate',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            })
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get('response', '').strip()
        else:
            print(f"Ollama API error: {result.stderr}", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("Ollama request timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        return None

def get_openrouter_suggestions(code_content, file_path):
    """Get code suggestions from OpenRouter API."""
    if not code_content:
        return None

    # Create a focused prompt for code review
    file_name = os.path.basename(file_path) if file_path else "code"
    prompt = f"""Review this code and provide ONLY the most critical issues:

File: {file_name}
```
{code_content}
```

List only severe issues (max 3):
- Security vulnerabilities
- Critical bugs that will cause crashes
- Major performance problems

Be extremely concise. One line per issue."""

    try:
        # Call OpenRouter API
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{
                "role": "system",
                "content": "You are a code reviewer. Be extremely concise and only report critical issues."
            }, {
                "role": "user",
                "content": prompt
            }],
            "temperature": 0.2,
            "max_tokens": 2048
        }

        result = subprocess.run([
            'curl', '-s', OPENROUTER_URL,
            '-H', f'Authorization: Bearer {OPENROUTER_API_KEY}',
            '-H', 'Content-Type: application/json',
            '-H', 'HTTP-Referer: https://8b.is?source=HookedOnCode',
            '-H', 'X-Title: Code Suggestions Hook',
            '-d', json.dumps(payload)
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content'].strip()
            elif 'error' in response:
                print(f"OpenRouter API error: {response['error']}", file=sys.stderr)
                return None
        else:
            print(f"OpenRouter API error: {result.stderr}", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("OpenRouter request timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error calling OpenRouter: {e}", file=sys.stderr)
        return None

def get_lm_studio_suggestions(code_content, file_path):
    """Get code suggestions from LM Studio."""
    if not code_content:
        return None

    # Create a prompt for code suggestions
    file_name = os.path.basename(file_path) if file_path else "code"
    prompt = f"""Analyze this code and provide suggestions for improvements:

File: {file_name}
```code
{code_content}
```

Please provide specific, actionable suggestions for:
1. Code quality improvements
2. Best practices
3. Potential bugs or issues
4. Performance optimizations
5. Security considerations

Keep suggestions concise and focused on the most important issues."""

    try:
        # Call LM Studio API (OpenAI-compatible)
        payload = {
            "model": LM_STUDIO_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }

        result = subprocess.run([
            'curl', '-s', f'{LM_STUDIO_HOST}/v1/chat/completions',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(payload)
        ], capture_output=True, text=True, timeout=60)  # LM Studio might be slower

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content'].strip()
            else:
                print(f"Unexpected LM Studio response format: {result.stdout}", file=sys.stderr)
                return None
        else:
            print(f"LM Studio API error: {result.stderr}", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("LM Studio request timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error calling LM Studio: {e}", file=sys.stderr)
        return None

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    # Only process code-writing tools
    code_tools = {"Write", "Edit", "MultiEdit"}
    if tool_name not in code_tools:
        sys.exit(0)  # Exit silently for non-code tools

    # Get file path (check both camelCase and snake_case)
    file_path = ""
    if tool_name == "Write":
        file_path = tool_input.get("file_path", "") or tool_input.get("filePath", "")
    elif tool_name in ["Edit", "MultiEdit"]:
        file_path = tool_input.get("file_path", "") or tool_input.get("filePath", "")

    # Check if it's a code file
    if not is_code_file(file_path):
        sys.exit(0)  # Exit silently for non-code files

    # Get the code content
    code_content = get_code_content(tool_name, tool_input, tool_response)

    if not code_content:
        sys.exit(0)  # No content to analyze

    # Get suggestions from the configured service
    if USE_SERVICE == "openrouter":
        suggestions = get_openrouter_suggestions(code_content, file_path)
    elif USE_SERVICE == "lm_studio":
        suggestions = get_lm_studio_suggestions(code_content, file_path)
    elif USE_SERVICE == "ollama":
        suggestions = get_ollama_suggestions(code_content, file_path)
    else:
        print(f"Unknown service: {USE_SERVICE}", file=sys.stderr)
        suggestions = None

    if suggestions:
        # Return suggestions as JSON for Claude to process
        output = {
            "continue": True,  # Don't block, just add context
            "systemMessage": f"Code suggestions for {os.path.basename(file_path)}:\n\n{suggestions}"
        }
        print(json.dumps(output))
    else:
        # No suggestions or error occurred, continue normally
        sys.exit(0)

if __name__ == "__main__":
    main()