# 🛑 Swarm System Error Log

> **Role**: Persistent Knowledge Base for Debugging
> **Usage**: Search this file (`search_codebase("Error Log")`) when encountering server or connectivity issues.

## 2026-01-20: MCP Server Connectivity

### 1. IPv6 vs IPv4 Mismatch (Windows)
- **Symptom**: `connectex: No connection could be made because the target machine actively refused it.` on `[::1]:8000`.
- **Cause**: Windows `localhost` often resolves to IPv6 `[::1]`, but uvicorn/fastapi typically binds to IPv4 `0.0.0.0` or `127.0.0.1`.
- **Fix**: Explicitly use `127.0.0.1` in `mcp_config.json`.
    ```json
    "serverUrl": "http://127.0.0.1:8000/sse"
    ```

### 2. Semantic Search Timeout / Crash
- **Symptom**: `httpx.ReadError` or Connection Closed during `audit_search.py`.
- **Cause**: The *first* run of `LocalEmbedding` (sentence-transformers) or heavy `GeminiEmbedding` batches can block the async event loop for too long (>60s), causing the HTTP client to time out or the server to be killed by the OS/Docker watchdog.
- **Fix**: 
    - **Increase Timeout**: Set client timeout to `300.0` seconds for initial indexing/search.
    - **Keyword Fallback**: Use `keyword_only=True` if the server is under heavy load or unstable.
    - **Logs**: Enable file logging in `server.py` to capture the stack trace (stdout often lost on crash).

### 3. Port Conflict
- **Symptom**: `[WinError 10048] Only one usage of each socket address...`
- **Cause**: Previous server instance didn't shut down cleanly (orphan process).
- **Fix**: Kill all python processes before restarting.
    ```powershell
    taskkill /F /IM python.exe
    ```

### 4. Server Not Found After Config Change
- **Symptom**: `server name swarm-orchestrator not found` after switching from SSE to Stdio.
- **Cause**: MCP Client (IDE) must be restarted to reload `mcp_config.json`.
- **Fix**: Completely restart the IDE/Client application.
- **Why**: The client caches the server configuration at startup. Changing `mcp_config.json` from `serverUrl` to `command`/`args` requires a full restart to take effect.
- **Verification**: After restart, `list_resources(swarm-orchestrator)` should succeed without EOF errors.
### 5. Docker Exec (Stdio) Troubleshooting
- **Symptom**: `server name swarm-orchestrator not found` OR `docker: exec: "swarm-mcp-server": container not found`.
- **Cause**: The container named in `mcp_config.json` is not running.
- **Fix**: 
    1. Start the container: `docker-compose up -d`.
    2. Verify name: `docker ps` to ensure it matches exactly (`swarm-mcp-server`).
    3. Stdio Tunnel: Ensur the `mcp_config.json` uses `exec -i` (interactive) to keep the stream open.
- **Benefit**: This mode bypasses all Windows-specific network issues (Firewalls/IPs) by using Docker's internal stdio piping.
