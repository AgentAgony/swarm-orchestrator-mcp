
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import List
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def load_dynamic_tools(mcp: FastMCP, tools_dir: Path = None) -> None:
    """
    Load dynamic tools from Python modules in the specified directory.
    
    Each tool module must export a `register(mcp: FastMCP)` function.
    
    Args:
        mcp: The FastMCP server instance
        tools_dir: Path to the dynamic tools directory (defaults to current dir)
    """
    if tools_dir is None:
        tools_dir = Path(__file__).parent
        
    if not tools_dir.exists():
        logger.warning(f"Dynamic tools directory not found: {tools_dir}")
        return

    logger.info(f"Scanning for dynamic tools in {tools_dir}")
    
    # Add tools dir to sys.path to allow imports
    str_tools_dir = str(tools_dir)
    if str_tools_dir not in sys.path:
        sys.path.insert(0, str_tools_dir)

    for file_path in tools_dir.glob("*.py"):
        if file_path.name == "__init__.py" or file_path.name == "loader.py":
            continue
            
        try:
            module_name = file_path.stem
            
            # Import module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                logger.warning(f"Failed to create spec for {file_path}")
                continue
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Look for register function
            if hasattr(module, "register") and callable(module.register):
                module.register(mcp)
                logger.info(f"Loaded dynamic tool module: {module_name}")
            else:
                logger.warning(f"Module {module_name} missing 'register(mcp)' function")
                
        except Exception as e:
            logger.error(f"Error loading dynamic tool {file_path}: {e}")
