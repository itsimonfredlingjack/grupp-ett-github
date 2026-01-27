#!/bin/bash
# PreToolUse hook: Block dangerous operations and detect credentials
# Called by Claude Code before executing Bash, Write, or Edit tools

set -euo pipefail

# Read hook input from stdin (JSON format)
HOOK_INPUT=$(cat)

# Extract tool name and input
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")
TOOL_INPUT=$(echo "$HOOK_INPUT" | jq -r '.tool_input // empty' 2>/dev/null || echo "")

# If jq fails or no input, allow operation
if [ -z "$TOOL_NAME" ]; then
    exit 0
fi

# Dangerous command patterns to block
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    "git reset --hard"
    "git push --force"
    "git push -f"
    "> /dev/sd"
    "mkfs\."
    "dd if=/dev/zero"
    "chmod -R 777"
    ":(){:|:&};"
    "wget.*|.*sh"
    "curl.*|.*sh"
)

# Credential patterns to detect
CREDENTIAL_PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "AKIA[0-9A-Z]{16}"
    "sk-[a-zA-Z0-9]{48}"
    "ghp_[a-zA-Z0-9]{36}"
    "xox[baprs]-[0-9a-zA-Z-]+"
)

# Check Bash commands
if [ "$TOOL_NAME" = "Bash" ]; then
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null || echo "")

    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if echo "$COMMAND" | grep -qE "$pattern"; then
            echo "{\"decision\": \"block\", \"reason\": \"Blocked dangerous command pattern: $pattern\"}"
            exit 0
        fi
    done
fi

# Check file content for credentials
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
    CONTENT=$(echo "$TOOL_INPUT" | jq -r '.content // .new_string // empty' 2>/dev/null || echo "")
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null || echo "")

    # Skip credential check for certain files
    case "$FILE_PATH" in
        *.md|*.txt|*.json|*.yaml|*.yml)
            # Allow documentation and config examples
            ;;
        *)
            for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
                if echo "$CONTENT" | grep -qiE "$pattern"; then
                    echo "{\"decision\": \"block\", \"reason\": \"Potential credentials detected. Pattern: $pattern\"}"
                    exit 0
                fi
            done
            ;;
    esac

    # Block modifications to protected paths
    PROTECTED_PATHS=(
        ".github/CODEOWNERS"
        ".claude/hooks/"
    )

    for protected in "${PROTECTED_PATHS[@]}"; do
        if [[ "$FILE_PATH" == *"$protected"* ]]; then
            # Allow initial creation, block modifications
            if [ -f "$FILE_PATH" ]; then
                echo "{\"decision\": \"block\", \"reason\": \"Cannot modify protected file: $FILE_PATH\"}"
                exit 0
            fi
        fi
    done
fi

# Allow operation (no output = allow)
exit 0
