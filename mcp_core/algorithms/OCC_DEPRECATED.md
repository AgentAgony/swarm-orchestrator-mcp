# OCC Validator - DEPRECATED

This algorithm was removed from the active codebase for the following reasons:

## Why It Was Removed

**Use Case Mismatch**: OCC (Optimistic Concurrency Control) is designed for multi-agent concurrent editing scenarios where:
- Multiple agents modify the same file simultaneously
- Race conditions need to be detected and merged
- AST-based conflict resolution is beneficial

**Reality for IDE Usage**:
- Single agent (Antigravity IDE) executing sequentially
- IDE has native file change detection and refresh
- Tool calls are serialized - no concurrent writes possible
- User edits are handled by IDE's own change detection

## What Was Kept

The file `occ_validator.py` remains in the codebase for reference, containing:
- AST-based merge logic for Python files
- Three-way merge detection
- Version-based collision detection

## If You Need OCC in the Future

**Scenarios where OCC would be useful:**
1. Multi-container Swarm deployment (multiple agents)
2. Background workers running concurrently with IDE
3. Distributed team collaboration with autonomous agents
4. Shared blackboard state across multiple processes

**To re-enable:**
1. Uncomment imports in `mcp_core/algorithms/__init__.py`
2. Add MCP tools to `server.py` (see git history)
3. Integrate with orchestrator for multi-agent tasks

## Files Removed

- `tests/algorithms/test_occ_merge.py` - AST merge tests
- `test_merge_debug.py` - Debug script
- `test_occ_mcp.py` - MCP integration test
- MCP tools from `server.py`: `read_file_with_version()`, `write_file_with_occ()`

---

*Removed: 2026-01-20*
*Reason: Feature focus for IDE-only usage*
