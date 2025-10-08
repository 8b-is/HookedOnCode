# Claude Code Ollama/LM Studio Code Suggestions Hook

This hook automatically analyzes code after it's written using Claude Code's Write, Edit, or MultiEdit tools and provides suggestions for improvements using a local LLM instance (Ollama or LM Studio).

## Prerequisites

Choose one of the following LLM backends:

### Option 1: Ollama
1. **Ollama installed and running**: Make sure Ollama is installed and accessible at `http://localhost:11434`
2. **Code model available**: Pull a coding model like CodeLlama:
   ```bash
   ollama pull codellama
   ```

### Option 2: LM Studio
1. **LM Studio installed and running**: Download from https://lmstudio.ai/
2. **Model downloaded**: Download the model `mradermacher/gpt-oss-6.0b-specialized-all-pruned-moe-only-7-experts-GGUF`
3. **Local server running**: Start LM Studio's local server (typically on port 1234)

## Setup

### 1. Place the Hook Script

Copy `code_suggestions_hook.py` to a location where Claude Code can access it. For project-specific hooks, place it in your project's `.claude/hooks/` directory:

```bash
mkdir -p .claude/hooks
cp code_suggestions_hook.py .claude/hooks/
```

### 2. Configure Claude Code Settings

Add the hook configuration to your Claude Code settings. You can add this to:

- `~/.claude/settings.json` (user-wide)
- `.claude/settings.json` (project-specific)
- `.claude/settings.local.json` (local project settings, not committed)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/code_suggestions_hook.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Replace `/path/to/code_suggestions_hook.py` with the actual path to your hook script.

### 3. Configure Environment Variables

Add the following to your `~/.bashrc`, `~/.zshrc`, or equivalent shell configuration:

```bash
# OpenRouter API (for code_suggestions_hook.py using OpenRouter)
export OPENROUTER_API_KEY="your-api-key-here"
export OPENROUTER_MODEL="x-ai/grok-code-fast-1"  # Optional, has default

# LM Studio (for local models)
export LM_STUDIO_HOST="http://localhost:1234"  # Optional, defaults to localhost:1234
export LM_STUDIO_MODEL="nousresearch/hermes-4-70b"  # Optional, has default
export SWALLOWMAID_MODEL="swallowmaid-8b-l3-sppo-abliterated@q8_0"  # For sexy_code_hook.py

# Ollama (alternative to LM Studio)
export OLLAMA_HOST="http://localhost:11434"  # Optional, has default
export OLLAMA_MODEL="codellama:7b"  # Optional, has default

# Service Selection (which backend to use)
export CODE_HOOK_SERVICE="openrouter"  # Options: openrouter, lm_studio, ollama
```

After adding these, reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

**Get your OpenRouter API key**: https://openrouter.ai/keys

### 4. Test the Hook

1. Start Claude Code in your project
2. Run `/hooks` to verify the hook is registered
3. Write or edit some code to trigger the hook
4. The hook should provide suggestions after code-writing operations

## Configuration Options

### Backend Selection

Configure which backend to use via environment variable:

```bash
export CODE_HOOK_SERVICE="openrouter"  # Options: openrouter, lm_studio, ollama
```

All configuration is done via environment variables (see Setup section above). No need to edit the hook scripts directly!

### LM Studio Setup

1. **Download the model**: In LM Studio, search for and download:
   `mradermacher/gpt-oss-6.0b-specialized-all-pruned-moe-only-7-experts-GGUF`

2. **Load the model**: Select the model in LM Studio and click "Load Model"

3. **Start local server**: Go to "Local Server" tab and start the server (default port 1234)

4. **Verify connection**: Test with:
   ```bash
   curl http://localhost:1234/v1/models
   ```

### Ollama Models

For Ollama, you can use various coding models:

### File Types

The hook automatically detects code files by extension. Supported file types include:

- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- C/C++ (.c, .cpp)
- C# (.cs)
- PHP (.php)
- Ruby (.rb)
- Go (.go)
- Rust (.rs)
- Swift (.swift)
- Kotlin (.kt)
- Scala (.scala)
- Clojure (.clj)
- Haskell (.hs)
- OCaml (.ml)
- Shell scripts (.sh, .bash, .zsh, .fish)
- PowerShell (.ps1)
- SQL (.sql)
- Web files (.html, .css, .scss, .sass, .less)
- Config files (package.json, requirements.txt, etc.)

## How It Works

1. **Trigger**: The hook runs after successful Write, Edit, or MultiEdit operations
2. **Detection**: Checks if the modified file contains code
3. **Analysis**: Sends the code to Ollama for analysis
4. **Suggestions**: Returns improvement suggestions to Claude
5. **Feedback**: Claude receives the suggestions and can incorporate them

## Troubleshooting

### Hook Not Running
- Check that the script is executable: `chmod +x code_suggestions_hook.py`
- Verify the path in settings.json is correct
- Run `/hooks` in Claude Code to see registered hooks
- Check Claude Code logs with `claude --debug`

### LM Studio Connection Issues
- Ensure LM Studio local server is running on port 1234
- Verify the model is loaded in LM Studio
- Check if the model name matches exactly (including the full path)
- Test LM Studio directly: `curl http://localhost:1234/v1/models`

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Verify the host/port configuration
- Test Ollama directly: `curl http://localhost:11434/api/tags`

### No Suggestions
- Check that you're editing code files (not text/markdown)
- Verify the Ollama model can generate responses
- Look for error messages in stderr

## Customization

### Custom Prompts

Modify the `get_ollama_suggestions` function to customize the analysis prompt:

```python
prompt = f"""Review this code for security vulnerabilities:

{code_content}

Focus on:
- SQL injection risks
- XSS vulnerabilities
- Authentication bypasses
- Input validation issues"""
```

### Different Analysis Types

Create multiple hook scripts for different types of analysis:

- `security_hook.py` - Security vulnerability scanning
- `performance_hook.py` - Performance optimization suggestions
- `style_hook.py` - Code style and formatting suggestions

### Conditional Analysis

Add conditions to only analyze certain files or under specific circumstances:

```python
# Only analyze Python files
if not file_path.endswith('.py'):
    sys.exit(0)

# Skip test files
if 'test' in file_path.lower():
    sys.exit(0)
```

## Security Considerations

- **API Keys**: All sensitive keys are stored in environment variables, not in code
- **Local LLMs**: When using Ollama or LM Studio, code stays on your local machine
- **OpenRouter**: When using OpenRouter, code is sent to their API (review their privacy policy)
- **No Secrets in Git**: API keys and sensitive configuration are never committed to the repository
- **Environment Variables**: Always store credentials in `.bashrc`/`.zshrc`, never in code
- Review the script before using in production environments