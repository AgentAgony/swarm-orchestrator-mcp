# process_task() - DEPRECATED

This MCP tool was removed from the active codebase for the following reasons:

## Why It Was Removed

**Use Case Mismatch**: `process_task()` was designed for orchestrated multi-agent workflows where:
- Natural language instructions need to be classified into task types
- Multiple algorithm workers compete or collaborate on problems
- Blackboard state tracks task progress across sessions
- Intent routing dispatches to specialized handlers (OCC, Z3, SBFL, etc.)

**Reality for IDE Usage**:
- Single agent (Antigravity IDE) knows which tool to call directly
- Classification layer adds latency without value
- Blackboard state is write-only (never queried by IDE)
- All capabilities available via direct tools

## What Was Removed

From `server.py`:
- `process_task()` MCP tool (~113 lines)
- `classify_task_intent()` helper function (~46 lines)
- **Total**: ~159 lines of indirection removed

## Direct Tool Alternatives

| Old (process_task) | New (Direct) |
|-------------------|--------------|
| `process_task("Search for auth logic")` | `search_codebase("auth logic")` |
| `process_task("Analyze data pipeline")` | `retrieve_context("data pipeline")` |
| `process_task("Debug test failure")` | `deliberate("debug test failure", context=...)` |
| `process_task("Refactor auth.py")` | `deliberate("refactor auth.py", context=...)` |

## If You Need It in the Future

**Scenarios where process_task would be useful:**
1. Multi-container Swarm with competing agents
2. Autonomous task queuing and prioritization
3. Long-running background workflows
4. Multi-hop reasoning with state persistence

**To re-enable:**
1. Restore from git history (commit before removal)
2. Update docstring to remove OCC references
3. Consider whether blackboard state adds value for your use case

## Architecture Preserved

The orchestrator internals (`orchestrator_loop.py`) remain unchanged:
- `Orchestrator.process_task(task_id)` still exists for CLI usage
- Algorithm routing logic intact
- Just the MCP wrapper was removed

---

*Removed: 2026-01-20*
*Reason: Feature focus for IDE-only usage*
*Related removals: OCC validator MCP tools*
