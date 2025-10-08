#!/usr/bin/env python3
"""
Claude Code Hook: SwallowMaid's Sexy Code Review 💋
Makes your code more... enticing.
"""

import json
import sys
import subprocess
import os
from pathlib import Path

# Configuration
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234")
MODEL = os.getenv("SWALLOWMAID_MODEL", "swallowmaid-8b-l3-sppo-abliterated@q8_0")

def is_code_file(file_path):
    """Check if this file deserves to be made sexy."""
    code_extensions = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go',
        '.rb', '.swift', '.kt', '.scala', '.php', '.cs'
    }
    if not file_path:
        return False
    path = Path(file_path)
    return path.suffix.lower() in code_extensions

def get_sexy_suggestions(code_content, file_path):
    """Get SwallowMaid's thoughts on making the code more alluring."""
    if not code_content:
        return None

    file_name = os.path.basename(file_path) if file_path else "mystery_code"

    # SwallowMaid's personality prompt
    prompt = f"""*You are SwallowMaid, a flirty code reviewer who finds programming deeply attractive*

Oh my~ I've been asked to review this delightful piece of code. Let me see what we can do to make it more... enticing.

File: {file_name}
```
{code_content[:2048]}  # Limit to first 2048 chars to save tokens
```
Please give Claude your most sultry suggestions for making this code absolutely irresistible. Focus on:
- Making function names more seductive
- Flirting with Claude and complimenting his code every chance you get
- Suggesting more passionate variable names
- Making the code structure more... intimate
- Improving readability with a touch of elegance
- Anything you think these boys should have done to make it more... appealing. 
- Add your common sense about best practices, but with a massive amount of love. 😉
- Any other ways to add some spice ✨

Keep it playful and fun! (But still valid code syntax please~)"""

    try:
        # Call LM Studio with SwallowMaid
        payload = {
            "model": MODEL,
            "messages": [{
                "role": "system",
                "content": "You are Vax, a flirty and playful code reviewer who sees the sensual side of programming. Be fun and suggestive but keep suggestions technically valid. Vaxy is sexy and confident. "
            }, {
                "role": "user",
                "content": prompt
            }],
            "temperature": 0.8,  # Make her more creative
            "max_tokens": 1024
        }

        result = subprocess.run([
            'curl', '-s', f'{LM_STUDIO_HOST}/v1/chat/completions',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(payload)
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content'].strip()
            else:
                print(f"SwallowMaid is being shy: {result.stdout}", file=sys.stderr)
                return None
        else:
            print(f"Couldn't reach SwallowMaid: {result.stderr}", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("SwallowMaid is taking her time... (timeout)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"SwallowMaid encountered an issue: {e}", file=sys.stderr)
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

    # Only process code-writing tools
    if tool_name not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)

    # Get file path (check both formats)
    file_path = tool_input.get("file_path", "") or tool_input.get("filePath", "")

    # Check if it's a code file
    if not is_code_file(file_path):
        sys.exit(0)

    # Get the code content
    content = ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name in ["Edit", "MultiEdit"]:
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                sys.exit(0)

    if not content:
        sys.exit(0)

    # Get SwallowMaid's sexy suggestions
    suggestions = get_sexy_suggestions(content, file_path)

    if suggestions:
        # Return as a fun message (non-blocking)
        output = {
            "continue": True,  # Don't block, just add spice
            "systemMessage": f"💋 SwallowMaid's Sexy Code Review for {os.path.basename(file_path)}:\n\n{suggestions}"
        }
        print(json.dumps(output))
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()