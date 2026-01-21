# Swarm Project Roadmap

## 🏁 Phase 1: Core Foundation (Completed)
- [x] **FastMCP Server**: Implemented generic MCP server shell.
- [x] **Orchestrator**: Dynamic task routing with blackboard architecture.
- [x] **Tool System**: Hot-reloadable `tools/` directory with `run_command` and file ops.
- [x] **Algorithm Workers**:
    - `DebateWorker` (Multi-perspective refactoring)
    - `GitWorker` (Autonomous version control)
    - `SearchEngine` (Hybrid Semantic + Keyword)

## 🧠 Phase 2: Intelligence & Memory (Completed)
- [x] **HippoRAG Integration**:
    - AST-based graph generation for Python.
    - Personalized PageRank for context retrieval.
    - Persistent graph caching (`.hipporag_cache`).
- [x] **Memory System**:
    - Active/Archive distinct storage.
    - `orient_context` and `refresh_memory` skills.
- [x] **Ochiai Fault Localization**: Statistical debugging tool.

## 📊 Phase 3: Visibility & Control (Completed)
- [x] **Dashboard UI**:
    - React + Vite + Glassmorphism design.
    - Real-time Task Board.
    - **Knowledge Graph Visualization** (Force-directed graph).
    - **Memory Inspector** (Provenance log & stack identity).
- [x] **Demo Mode**:
    - Fallback mock data for offline presentation.
    - Dedicated "Architecture" diagram in Documentation view.

## 🚀 Phase 4: Future Horizons (Backlog)
- [ ] **Multi-Language Support**:
    - Add Tree-sitter parsers for Rust, Go, and Java to HippoRAG.
- [ ] **Advanced Verification**:
    - Integrate `Z3` SMT solver for formal logic verification of critical algorithms.
- [ ] **Collaborative Swarm**:
    - Enable multi-server communication (Swarm-to-Swarm protocol).
- [ ] **Neural Bug Detection**:
    - Train a small ML model on the `provenance` log to predict future failure points.

---
*Last Updated: 2026-01-21*
