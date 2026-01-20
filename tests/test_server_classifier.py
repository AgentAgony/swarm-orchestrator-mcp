
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from server import classify_task_intent

@pytest.mark.parametrize("instruction,expected_key", [
    # Debug / SBFL
    ("Debug why test_auth.py is failing", "tests_failing"),
    ("Fix the error in login module", "tests_failing"),
    ("Why is the build broken?", "tests_failing"),
    
    # Verification / Z3
    ("Verify that get_user returns a user", "verification_required"),
    ("Prove that tax is never negative", "verification_required"),
    
    # Context / HippoRAG
    ("Analyze the dependency graph", "context_needed"),
    ("Explain how auth works", "context_needed"),
    ("Understand the context of this change", "context_needed"),
    
    # Concurrent / CRDT
    ("Merge changes from main", "concurrent_edits"),
    ("Resolve conflict in user.py", "concurrent_edits"),
    
    # Refactor / OCC
    ("Refactor user.py to use async", "conflicts_detected"),
    ("Rewrite the logging module", "conflicts_detected"),
    
    # Git Workflow
    ("Commit changes to repo", "git_commit_ready"),
    ("Commit and push changes", "git_auto_push"),
    ("Deploy to production", "git_auto_push"),
    ("Create a Pull Request", "git_create_pr"),
    ("Make a PR for this feature", "git_create_pr"),
])
def test_classifier_keywords(instruction, expected_key):
    """Test that keywords trigger the correct flags."""
    flags = classify_task_intent(instruction)
    assert flags.get(expected_key) is True, f"Failed to match '{expected_key}' in '{instruction}'"

def test_classifier_multi_intent():
    """Test that multiple intents can be detected."""
    # "Debug" -> tests_failing
    # "Analyze" -> context_needed
    instruction = "Analyze the error logs to debug the failure"
    flags = classify_task_intent(instruction)
    
    assert flags.get("tests_failing") is True
    assert flags.get("context_needed") is True

def test_classifier_case_insensitivity():
    """Test that classification is case insensitive."""
    flags = classify_task_intent("DEBUG THE FAILURE")
    assert flags.get("tests_failing") is True

def test_no_intent():
    """Test that neutral instructions return empty flags."""
    flags = classify_task_intent("Hello world")
    assert flags == {}
