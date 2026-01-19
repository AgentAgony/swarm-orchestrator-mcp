import inspect
from fastmcp import FastMCP

print("FastMCP.run signature:")
try:
    print(inspect.signature(FastMCP.run))
except Exception as e:
    print(e)
    
print("\nFastMCP attributes:")
print([x for x in dir(FastMCP) if 'run' in x])
