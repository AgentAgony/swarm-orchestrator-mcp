
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp_core.tools.system import register_system_tools
from fastmcp import FastMCP, Context

# Mock Classes for FastMCP Context
class MockSession:
    def __init__(self):
        self.send_sampling_request = AsyncMock()

class MockContext:
    def __init__(self):
        self.session = MockSession()
        self.request = MagicMock()

@pytest.mark.asyncio
async def test_consult_reasoning_model_thinking():
    """Verify 'thinking' strategy maps to intelligence: high."""
    
    # 1. Setup Mock
    mcp = FastMCP("Test")
    register_system_tools(mcp)
    
    # Extract the registered tool function
    # Note: FastMCP stores tools in mcp._tool_manager or similar, but we can test the logic directly 
    # if we could import the inner function.
    # Instead, we will assume we can access it or we'll just replicate the import for testing.
    
    from mcp_core.tools.system import register_system_tools
    
    # Capture the decorator to get the function
    tools = {}
    mcp.tool = lambda: lambda f: tools.update({f.__name__: f})
    register_system_tools(mcp)
    
    tool_func = tools["consult_reasoning_model"]
    ctx = MockContext()
    
    # 2. Mock Response
    ctx.session.send_sampling_request.return_value = MagicMock(content=MagicMock(text="I am thinking deeply..."))
    
    # 3. Call Tool
    result = await tool_func(prompt="Solve world peace", strategy="thinking", ctx=ctx)
    
    # 4. Verify
    assert "I am thinking deeply" in result
    
    # Check arguments sent to session
    call_args = ctx.session.send_sampling_request.call_args[1] # kwargs
    assert call_args["model_preferences"] == {"intelligence": "high", "cost": "high"}
    print("\n✅ Strategy 'thinking' mapped correctly.")

@pytest.mark.asyncio
async def test_consult_reasoning_model_fast():
    """Verify 'fast' strategy maps to speed: high."""
    
    mcp = FastMCP("Test")
    tools = {}
    mcp.tool = lambda: lambda f: tools.update({f.__name__: f})
    register_system_tools(mcp)
    
    tool_func = tools["consult_reasoning_model"]
    ctx = MockContext()
    ctx.session.send_sampling_request.return_value = MagicMock(content=MagicMock(text="Quick response."))
    
    await tool_func(prompt="Hi", strategy="fast", ctx=ctx)
    
    call_args = ctx.session.send_sampling_request.call_args[1]
    assert call_args["model_preferences"] == {"speed": "high", "cost": "low"}
    print("✅ Strategy 'fast' mapped correctly.")

if __name__ == "__main__":
    # verification harness
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_consult_reasoning_model_thinking())
        loop.run_until_complete(test_consult_reasoning_model_fast())
        print("\n🎉 Al sampling routing tests passed!")
    finally:
        loop.close()
