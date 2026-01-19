# Use Python as the sole runtime (Swarm v3.0)
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
# Note: z3-solver and other wheels are installed here
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 8000

# Verify v3.0 installation works (imports algorithms)
RUN python -c "from mcp_core.algorithms import OCCValidator; print('Swarm v3.0 Ready')"

# Default command: Run MCP server
CMD ["fastmcp", "run", "server.py", "--host", "0.0.0.0", "--port", "8000"]
