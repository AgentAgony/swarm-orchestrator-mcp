
import os
import sys
import logging
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_system_tools(mcp: FastMCP):
    """Register system-level management tools."""
    
    @mcp.tool()
    def restart_server(reason: str = "Manual restart") -> str:
        """
        Trigger a safe restart of the MCP server.
        
        This is used to reload dynamic tools or apply configuration changes.
        The server will exit with code 100, which should be handled by 
        the container manager to restart the process.
        
        Args:
            reason: Description of why the restart was triggered
        """
        logger.warning(f"Server restart triggered: {reason}")
        
        # Flush logs
        logging.shutdown()
        
        # Exit with special code 100
        # We use a deferred exit to allow the tool response to return first?
        # Actually, if we exit immediately, the client might get a connection error.
        # But FastMCP doesn't support async background tasks easily.
        # We'll just exit and let the client handle reconnection.
        sys.exit(100)

    @mcp.tool()
    def create_tool_file(filename: str, code: str, description: str) -> str:
        """
        Create a new dynamic tool file and document it in the changelog.
        
        This tool allows agents to autonomously extend the server's capabilities.
        It performs safety checks, writes the file to the dynamic tools directory,
        and updates the project changelog.
        
        Args:
            filename: Name of the file (e.g., 'tool_analytics.py'). Must end in .py.
            code: Complete Python code. Must include a `def register(mcp):` function.
            description: Short description of the tool's purpose for the Changelog.
            
        Returns:
            Status message. If successful, you should usually call restart_server() next.
        """
        import re
        from pathlib import Path
        
        # 1. Validation
        if not filename.endswith(".py"):
            return "❌ Error: Filename must end with .py"
        
        # Check for required signature (simple string check is safer than parsing for now)
        if "def register" not in code:
            return "❌ Error: Code must contain a 'def register(mcp: FastMCP):' function."
            
        if "fastmcp" not in code and "FastMCP" not in code:
             return "❌ Error: Code seems to be missing FastMCP import or usage."

        # 2. Path Resolution
        # mcp_core/tools/system.py -> mcp_core/tools -> mcp_core -> swarm root
        current_file = Path(__file__)
        tools_dir = current_file.parent # mcp_core/tools
        dynamic_dir = tools_dir / "dynamic"
        server_root = tools_dir.parent.parent # swarm/
        
        target_path = dynamic_dir / filename
        
        try:
            # 3. Write Tool File
            target_path.write_text(code, encoding="utf-8")
            logger.info(f"Created dynamic tool: {target_path}")
            
            # 4. Update Changelog
            changelog_path = server_root / "CHANGELOG.md"
            if changelog_path.exists():
                content = changelog_path.read_text(encoding="utf-8")
                
                # Dynamic Changelog Entry
                entry = f"- **New Tool ({filename})**: {description}"
                
                # Regex to find the first "### Added" section under a version header
                # Or if not found, find the first version header and insert ### Added
                
                # Look for first version header like "## [3.0.0]"
                version_match = re.search(r"^## \[[^\]]+\]", content, re.MULTILINE)
                
                if version_match:
                    version_idx = version_match.end()
                    # Search for "### Added" between here and the next "## ["
                    # Limiting scope to next 50 lines to be safe? 
                    # Simpler: just insert "### Added" right after the version header if strictly needed,
                    # but let's try to be cleaner.
                    
                    # Naive insertion: Find first "### Added"
                    added_match = re.search(r"^### Added", content[version_idx:], re.MULTILINE)
                    
                    if added_match:
                        # Found existing Added section, insert after it
                        insert_pos = version_idx + added_match.end()
                        new_content = (
                            content[:insert_pos] 
                            + f"\n{entry}" 
                            + content[insert_pos:]
                        )
                    else:
                        # No Added section in latest version, create it
                        new_content = (
                            content[:version_idx]
                            + f"\n\n### Added\n{entry}"
                            + content[version_idx:]
                        )
                        
                    changelog_path.write_text(new_content, encoding="utf-8")
                    logger.info("Updated CHANGELOG.md")
                else:
                    logger.warning("Could not find version header in CHANGELOG.md")
            
            return f"✅ Tool '{filename}' created successfully and changelog updated.\nRun `restart_server()` to activate."
            
        except Exception as e:
            logger.error(f"Failed to create tool: {e}")
            return f"❌ Failed to create tool: {str(e)}"

    @mcp.tool()
    def create_skill_file(skill_name: str, instructions: str) -> str:
        """
        Create an Antigravity Skill artifact for the IDE agent.
        
        This teaches the frontend agent how to use a backend tool or workflow.
        
        Args:
            skill_name: Name of the skill (e.g., 'CalculateStats'). Directory will be created.
            instructions: Content of the SKILL.md file (Markdown).
            
        Returns:
            Status message.
        """
        from pathlib import Path
        
        # Resolve path to .agent/skills/ relative to server root
        # mcp_core/tools/system.py -> mcp_core/tools -> mcp_core -> swarm root
        current_file = Path(__file__)
        server_root = current_file.parent.parent.parent # swarm/
        
        # Target: .agent/skills/<skill_name>/SKILL.md
        # Note: In a real deployment, this path might need configuration to point to the user's workspace
        # For now, we assume the server is running in the project root or has access to it.
        # If running in Docker, we might need a mounted volume for .agent
        
        skills_dir = server_root / ".agent" / "skills" / skill_name
        
        try:
            if not skills_dir.exists():
                skills_dir.mkdir(parents=True, exist_ok=True)
                
            skill_file = skills_dir / "SKILL.md"
            skill_file.write_text(instructions, encoding="utf-8")
            
            logger.info(f"Created skill artifact: {skill_file}")
            return f"✅ Skill '{skill_name}' created at {skill_file}"
            
        except Exception as e:
            logger.error(f"Failed to create skill: {e}")
            return f"❌ Failed to create skill: {str(e)}"
