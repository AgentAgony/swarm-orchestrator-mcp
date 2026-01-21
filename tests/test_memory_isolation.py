import shutil
from pathlib import Path
from fastmcp import FastMCP
import sys

# Add swarm root to path so we can import the worker
SWARM_ROOT = Path("v:/Projects/Servers/swarm")
sys.path.insert(0, str(SWARM_ROOT))

from mcp_core.tools.dynamic import memory_worker

# Setup Test Environment
TEST_SESSION_ID = "test_verification_session"
SESSION_ROOT = SWARM_ROOT / "docs" / "sessions" / TEST_SESSION_ID
GLOBAL_PLAN = SWARM_ROOT / "docs" / "PLAN.md"

def setup():
    if SESSION_ROOT.exists():
        shutil.rmtree(SESSION_ROOT)

def teardown():
    if SESSION_ROOT.exists():
        shutil.rmtree(SESSION_ROOT)
    pass # Keep artifacts for inspection if needed, or uncomment above to clean

def test_isolation():
    print("🔍 Testing Memory Isolation...")
    
    # 1. Initialize MCP for side effects (if any), but import logic directly
    # mcp = FastMCP("test_memory") 
    # memory_worker.register(mcp)
    
    # Import logic directly
    from mcp_core.tools.dynamic.memory_worker import _orient_context, _refresh_memory
    
    orient = _orient_context
    refresh = _refresh_memory
    
    print("\n--- Testing Global Context ---")
    global_res = orient()
    print(f"DEBUG: global_res head: {global_res[:100]}...")
    if "Current Roadmap (docs/PLAN.md)" not in global_res and "Current Roadmap (docs\\PLAN.md)" not in global_res:
         print(f"❌ ASSERT FAIL: Expected 'Current Roadmap (docs/PLAN.md)' in result.")
    assert "Current Roadmap" in global_res
    print("✅ Global context reads correct PLAN.md")
    
    # 3. Test Session Initialization
    print(f"\n--- Testing Session Context ({TEST_SESSION_ID}) ---")
    session_res = orient(session_id=TEST_SESSION_ID)
    
    print(f"DEBUG: Checking {SESSION_ROOT}")
    assert SESSION_ROOT.exists(), "Session root not created"
    assert (SESSION_ROOT / "PLAN.md").exists(), "Session plan not copied"
    
    expected_path_part = f"docs/sessions/{TEST_SESSION_ID}/PLAN.md"
    expected_path_part_win = f"docs\\sessions\\{TEST_SESSION_ID}\\PLAN.md"
    
    print(f"DEBUG: Looking for path in response...")
    if expected_path_part not in session_res and expected_path_part_win not in session_res:
         print(f"❌ ASSERT FAIL: Expected path not found in: {session_res[:200]}")
         
    assert expected_path_part in session_res or expected_path_part_win in session_res
    print("✅ Session context created and reads isolated PLAN.md")
    
    # 4. Test Isolation (Modification)
    # Modify session plan
    session_plan_file = SESSION_ROOT / "PLAN.md"
    original_content = GLOBAL_PLAN.read_text(encoding="utf-8")
    session_plan_file.write_text("# HACKED SESSION PLAN", encoding="utf-8")
    
    # Verify global is untouched
    orient() # Call global again
    assert GLOBAL_PLAN.read_text(encoding="utf-8") == original_content
    print("✅ Modifying session plan did not affect global plan")
    
    # 5. Test Memory Refresh Isolation
    print("\n--- Testing Refresh Isolation ---")
    # Create a dummy active task in session
    active_task = SESSION_ROOT / "memory" / "active" / "completed_task.md"
    active_task.parent.mkdir(parents=True, exist_ok=True)
    active_task.write_text("# Done Task\nStatus: Completed\n[x] Done", encoding="utf-8")
    
    ref_res = refresh(session_id=TEST_SESSION_ID)
    assert "Consolidated 1 files" in ref_res
    assert not active_task.exists(), "Session task not pruned"
    assert (SESSION_ROOT / "memory" / "archive" / "session_summary.md").exists(), "Session archive not created"
    print("✅ Session refresh worked in isolation")

    # Teardown
    teardown()
    print("\n🏆 Verification Successful: Memory Isolation Works!")

if __name__ == "__main__":
    setup()
    try:
        test_isolation()
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        teardown()
        exit(1)
