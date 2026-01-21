import logging
import os
from pathlib import Path
from typing import List
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def orient_context(session_id: str = None) -> str:
        """
        Orient the current session using the memory systems defined in skill-memory-orient.md.
        
        Usage Heuristics:
        - Use when: Session start, context reset, or before starting a complex task.
        - Returns: A summary of the current roadmap, active tasks, and context triggers.
        
        Args:
            session_id: Optional unique identifier for the session. If provided, creates an isolated memory environment.
        """
        return _orient_context(session_id)

    @mcp.tool()
    def refresh_memory(session_id: str = None) -> str:
        """
        Consolidate and prune active memory files per skill-memory-refresh.md.
        
        Usage Heuristics:
        - Use when: Too many active task files exist (>10) or at session end.
        - Effect: Moves completed task insights to archive and deletes raw files.
        
        Args:
            session_id: Optional unique identifier for the session.
        """
        return _refresh_memory(session_id)

def _orient_context(session_id: str = None) -> str:
    import shutil
    # Logic extracted for testability
    swarm_root = Path(__file__).parent.parent.parent.parent
    
    # Determine paths based on session_id
    if session_id:
        session_root = swarm_root / "docs" / "sessions" / session_id
        plan_path = session_root / "PLAN.md"
        active_dir = session_root / "memory" / "active"
        
        # Initialize session if not exists
        if not session_root.exists():
            session_root.mkdir(parents=True, exist_ok=True)
            active_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy global PLAN.md if it exists, else create empty
            global_plan = swarm_root / "docs" / "PLAN.md"
            if global_plan.exists():
                shutil.copy(global_plan, plan_path)
            else:
                plan_path.write_text("# Session Plan\n", encoding="utf-8")
                
            info_header = f"🧠 Swarm Orienting Protocol Results (Session: {session_id}):\n"
        else:
            info_header = f"🧠 Swarm Orienting Protocol Results (Session: {session_id}):\n"
    else:
        # Global Mode
        plan_path = swarm_root / "docs" / "PLAN.md"
        active_dir = swarm_root / "docs" / "ai" / "memory" / "active"
        info_header = "🧠 Swarm Orienting Protocol Results (Global):\n"
    
    info = [info_header]
    
    # 1. Load Roadmap
    if plan_path.exists():
        plan_content = plan_path.read_text(encoding="utf-8")
        # Extract high-level goals (first 20 lines)
        info.append(f"📍 Current Roadmap ({plan_path.relative_to(swarm_root)}):")
        info.append("\n".join(plan_content.splitlines()[:20]))
        info.append("...\n")
    else:
        info.append("⚠️ PLAN.md not found.")
        
    # 2. Identify Active Tasks
    if active_dir.exists():
        active_files = list(active_dir.glob("*.md"))
        info.append(f"🔥 Active Task Files ({len(active_files)} found):")
        for f in active_files:
            # Get the first line/title
            first_line = "No title"
            try:
                with open(f, "r", encoding="utf-8") as f_obj:
                    first_line = f_obj.readline().strip().replace("# ", "")
            except Exception:
                pass
            info.append(f"  • {f.name}: {first_line}")
    else:
        info.append("ℹ️ No active/ directory found.")
        
    return "\n".join(info)

def _refresh_memory(session_id: str = None) -> str:
    swarm_root = Path(__file__).parent.parent.parent.parent
    
    if session_id:
        base_dir = swarm_root / "docs" / "sessions" / session_id
        active_dir = base_dir / "memory" / "active"
        archive_path = base_dir / "memory" / "archive" / "session_summary.md"
    else:
        active_dir = swarm_root / "docs" / "ai" / "memory" / "active"
        archive_path = swarm_root / "docs" / "ai" / "memory" / "archive" / "2026_01_Summary.md"
    
    if not active_dir.exists():
        return f"❌ active/ directory not found at {active_dir}."
        
    active_files = list(active_dir.glob("*.md"))
    to_prune = []
    summary_entries = []
    
    for f in active_files:
        # Safety guards
        if any(p in f.name for p in ["MASTER_PLAN", "ERROR_LOG", "[ACTIVE]"]):
            continue
            
        content = f.read_text(encoding="utf-8")
        # Check if completed
        if "[x]" in content or "status: completed" in content.lower():
            # Extract simple summary (first 500 chars)
            summary_entries.append(f"### {f.name}\n{content[:500]}...\n")
            to_prune.append(f)
            
    if not summary_entries:
        return "✅ No completed tasks found to refresh."
        
    # Append to archive
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with open(archive_path, "a", encoding="utf-8") as a:
        a.write("\n" + "\n".join(summary_entries))
        
    # Prune
    for f in to_prune:
        f.unlink()
        
    return f"📦 Memory Refreshed: Consolidated {len(summary_entries)} files into {archive_path.name} and pruned them."
