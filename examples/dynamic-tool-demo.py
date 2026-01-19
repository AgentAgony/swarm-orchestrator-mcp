
"""
Toolsmith Demo Script

This script demonstrates how an AI agent (simulated here) would use the 
Toolsmith capability to create a new tool dynamically.

Workflow:
1. Agent identifies need (missing 'calculate_stats' tool)
2. Agent writes tool code
3. Agent calls `create_tool_file`
4. Server restarts (simulated log message)
"""

import sys
from pathlib import Path

# Mocking the interaction for demo purposes
# In reality, this code comes from the LLM based on worker_prompts.prompt_toolsmith

TOOL_FILENAME = "tool_stats.py"
TOOL_DESCRIPTION = "Calculates basic statistics (mean, median) for a list of numbers."

TOOL_CODE = """
from typing import List, Dict
from fastmcp import FastMCP
import statistics

def register(mcp: FastMCP):
    @mcp.tool()
    def calculate_stats(numbers: List[float]) -> Dict[str, float]:
        \"\"\"
        Calculates basic statistics for a list of numbers.

        Usage Heuristics:
        - Use this when: the user asks for "average", "mean", or "stats" of a dataset.
        - Do NOT use this for: complex regression or ML models.
        \"\"\"
        if not numbers:
            return {"error": "Empty list"}
            
        return {
            "mean": statistics.mean(numbers),
            "median": statistics.median(numbers),
            "min": min(numbers),
            "max": max(numbers),
            "count": len(numbers)
        }
"""


SKILL_INSTRUCTIONS = """# Skill: Calculate Stats
## Description
This skill teaches the IDE agent how to calculate basic statistics.

## When to use this skill
- Use when the user presents a list of numbers and asks for summaries.
- Use when debugging performance metrics.

## Usage
Call `calculate_stats(numbers=[...])`.
"""

def run_demo():
    print(f"🤖 Toolsmith Agent: Analyzing request...")
    print(f"📊 ROI Check: Task 'calc stats' performed 5 times manually. ROI: HIGH.")
    
    print("\n🛑 PERMISSION GATE: Requesting approval...")
    print('   "I want to build a tool for [Calculate Basics Stats] because [It saves 2 mins per analysis]. Proceed?"')
    print("   User: 'Proceed'")
    
    print(f"\n📝 Generating code for '{TOOL_FILENAME}' (with Heuristics)...")
    
    # 1. Connect to MCP (Simulation)
    # In a real scenario, this is an MCP tool call:
    # use_tool("create_tool_file", filename=..., code=...)
    
    print("-" * 40)
    print(f"FILENAME: {TOOL_FILENAME}")
    print(f"DESCRIPTION: {TOOL_DESCRIPTION}")
    print("CODE:")
    print(TOOL_CODE.strip())
    print("-" * 40)
    
    print("\n🚀 Executing `create_tool_file` tool call...")
    print("   [Server] Created dynamic tool: mcp_core/tools/dynamic/tool_stats.py")
    print("   [Server] Updated CHANGELOG.md")
    
    print("\n📘 Synthesizing Skill Artifact...")
    print(f"   [Server] Created skill artifact: .agent/skills/CalculateStats/SKILL.md")
    print("-" * 40)
    print("SKILL CONTENT:")
    print(SKILL_INSTRUCTIONS.strip())
    print("-" * 40)

    print("\n✅ Demo Complete. To run this for real:")
    print("1. Start Swarm server")
    print("2. Ask: 'Create a new tool called tool_stats.py and teach me how to use it'")
    
if __name__ == "__main__":
    run_demo()
