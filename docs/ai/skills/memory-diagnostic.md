# Memory Diagnostic Skill

Routing new errors through previous knowledge to find instant solutions.

---

## When to Use This Skill

- As the VERY FIRST STEP when a command fails.
- When a tool returns an EOF, Timeout, or Permission error.

## The Diagnostic Routing

### Step 1: Query the Knowledge Base
Run a targeted keyword search against the Error Log:
```powershell
search_codebase("Swarm Error Log", keyword_only=True)
```

### Step 2: Compare Patterns
- Does the current error message (e.g., `Address already in use`) match a section in `00_ERROR_LOG.md`?
- If YES: Apply the documented "Fix" immediately. Do NOT troubleshoot from scratch.

### Step 3: Update on Delta
If the error is slightly different (e.g., a new port number or a different Windows error code):
1. Apply the fix.
2. Update the `00_ERROR_LOG.md` with the new variation to strengthen the memory.

## Routing Logic
- **Known Problem**: Fixed in 1 tool call.
- **New Problem**: Debug → Resolve → Memory Log.
