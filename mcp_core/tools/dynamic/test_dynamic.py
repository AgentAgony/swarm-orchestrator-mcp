
from fastmcp import FastMCP

def register(mcp: FastMCP):
    @mcp.tool()
    def hello_dynamic(name: str) -> str:
        """Returns a greeting from the dynamic tool system."""
        return f"Hello {name}, I was loaded dynamically!"
