---
name: jules-review
description: Request deep code review from Jules (Google's AI coding agent). Use before merge or after major features.
args: none (reviews current branch changes)
---

# Jules Deep Review Skill

This skill triggers an **asynchronous** code review using Jules (Google's Gemini-based coding agent). Use it for thorough security, architecture, and best practices review.

## When to Use

- Before merging a feature branch
- After completing a major feature
- When you want a "second opinion" on complex code
- For security-sensitive changes

## Prerequisites

- Jules CLI installed (`jules` command available)
- Logged in to Jules (`jules login`)
- Changes committed (reviews the diff against main)

## Workflow

### Step 1: Check Prerequisites

```bash
# Verify Jules CLI
which jules || echo "ERROR: jules not installed"

# Check login status
jules remote list --session 2>&1 | head -5
```

If not logged in, run `jules login` first.

### Step 2: Collect Context

Read the current task and gather diff:

```bash
# Get branch name
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Get diff against main
DIFF=$(git diff main...HEAD)

# Read task context
TASK_FILE=""
for f in docs/CURRENT_TASK.md CURRENT_TASK.md; do
  [[ -f "$f" ]] && TASK_FILE="$f" && break
done
```

### Step 3: Build Review Prompt

Create a structured prompt for Jules:

```
Review the following code changes for:

## Security
- OWASP Top 10 vulnerabilities
- Input validation issues
- Authentication/authorization flaws
- Secrets exposure

## Architecture
- Design pattern violations
- SOLID principle adherence
- Separation of concerns
- Dependency issues

## Performance
- N+1 queries
- Memory leaks
- Inefficient algorithms
- Missing caching opportunities

## Code Quality
- Code smells
- Duplicated logic
- Naming conventions
- Error handling

## Task Context
[Contents of CURRENT_TASK.md]

## Changes (Diff)
[Git diff output]

---

Provide structured feedback as:
1. CRITICAL issues (must fix before merge)
2. WARNINGS (should fix)
3. SUGGESTIONS (nice to have)

For each issue, include:
- File and line number
- Description of the problem
- Suggested fix
```

### Step 4: Start Jules Session

```bash
# Create review request file
cat > .claude/reviews/jules_request.md << 'EOF'
[Full prompt from Step 3]
EOF

# Start Jules session
SESSION_OUTPUT=$(cat .claude/reviews/jules_request.md | jules new 2>&1)
echo "$SESSION_OUTPUT"

# Extract session ID (if shown)
SESSION_ID=$(echo "$SESSION_OUTPUT" | grep -oE '[0-9]{6,}' | head -1)
echo "Session ID: $SESSION_ID"
```

### Step 5: Wait for Results

Jules runs asynchronously. Options:

**Option A: Poll manually**
```bash
# Check session status
jules remote list --session

# When complete, pull results
jules remote pull --session $SESSION_ID
```

**Option B: Use TUI**
```bash
# Open Jules TUI to monitor
jules
```

**Option C: Set timeout and poll**
```bash
# Poll every 30 seconds for up to 10 minutes
TIMEOUT=600
INTERVAL=30
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
  STATUS=$(jules remote list --session 2>&1 | grep "$SESSION_ID")
  if echo "$STATUS" | grep -q "completed\|done\|finished"; then
    echo "Review complete!"
    jules remote pull --session $SESSION_ID > .claude/reviews/jules_response.md
    break
  fi
  echo "Waiting... ($ELAPSED/$TIMEOUT seconds)"
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done
```

### Step 6: Process Results

Read and act on the review:

```bash
cat .claude/reviews/jules_response.md
```

**For CRITICAL issues:**
- Fix immediately before continuing
- Re-run tests after fixes

**For WARNINGS:**
- Fix if quick (< 5 min)
- Otherwise create follow-up ticket

**For SUGGESTIONS:**
- Note for future reference
- Consider during refactoring

### Step 7: Log in CURRENT_TASK.md

Add review summary:

```markdown
### Jules Deep Review
- **Session ID:** [ID]
- **Status:** [completed/timeout]
- **Critical Issues:** [count]
- **Warnings:** [count]
- **Suggestions:** [count]
- **Action Taken:** [fixed X, deferred Y to ticket Z]
```

## Quick Reference

```bash
# One-liner to start review
git diff main...HEAD | jules new "Review this diff for security, performance, and code quality issues. Provide structured feedback."

# Check status
jules remote list --session

# Get results
jules remote pull --session [ID]
```

## Important Notes

1. **Async nature**: Jules may take 1-10 minutes depending on diff size
2. **Cost**: Jules uses API credits - use thoughtfully
3. **Not a replacement**: This supplements, not replaces, local tests and human review
4. **Context limit**: Very large diffs may be truncated

## Error Handling

- **"Not logged in"**: Run `jules login`
- **"Rate limited"**: Wait and retry, or reduce diff size
- **"Session not found"**: Check `jules remote list --session` for correct ID
- **Timeout**: Review may still complete - check TUI with `jules`
