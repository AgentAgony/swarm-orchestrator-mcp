# Changelog

All notable changes to Project Swarm will be documented in this file.

## [3.0.0] - 2026-01-18

### 🚀 Major: Algorithmic Blackboard Upgrade

Tranformed Swarm from a standard LLM orchestrator to an **Algorithmic Blackboard** with 7 specialized deterministic workers.

### Added

- **7 New Algorithm Workers** (`mcp_core/algorithms/`)
  - **HippoRAG:** AST-based graph retrieval with PageRank.
  - **OCC Validator:** Optimistic Concurrency Control for atomic file writes.
  - **CRDT Merger:** Conflict-Free Replicated Data Types for concurrent edits.
  - **Weighted Voting:** Consensus engine with Elo ratings.
  - **Debate Engine:** Sparse-topology debate system.
  - **Z3 Verifier:** Formal verification using SMT solver.
  - **Ochiai Localizer:** Automated fault localization (SBFL).

- **New CLI Commands** (`orchestrator.py`)
  - `retrieve <query>`: Deep context retrieval via HippoRAG.
  - `debug --test-cmd`: Auto-locate bugs in failing tests.
  - `verify <func>`: Generate Z3 verification guides.
  - `benchmark`: Validate 3x velocity improvements.

- **Comprehensive Test Suite** (`tests/algorithms/`)
  - ~80 new tests covering all algorithm workers.
  - 95% coverage target.

### Changed

- **Task Dispatch:** `Orchestrator` now routes tasks to algorithms based on flags (`context_needed`, `conflicts_detected`, etc.) before falling back to LLM agents.
- **Project Structure:** Moved core logic to `mcp_core/` with dedicated `algorithms/` submodule.

## [2.1.0] - 2026-01-01

- **Python-Native Search Engine**
  - Replaced Node.js search with pure Python implementation.
  - Added Hybrid Search (Semantic + Keyword).

## [2.0.0] - Previous

- Node.js MCP server architecture.
- Initial Python orchestrator prototype.
