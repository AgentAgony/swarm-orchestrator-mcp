# MCP Configuration Examples

This directory contains example configurations for connecting to the Swarm MCP server from various clients.

## 📁 Configuration Files

### [`claude_desktop_config.json`](./claude_desktop_config.json)
**Multi-server setup** with Swarm + Docker + GitHub + Filesystem.

**Use case:** Full-featured development environment with:
- Swarm for code analysis and algorithmic operations
- Docker for isolated execution
- GitHub for repository management
- Filesystem for local file access

**Installation:**
1. Copy contents to your Claude Desktop config:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **MacOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Ensure Swarm Docker container is running:
   ```bash
   cd v:\Projects\Servers\swarm
   docker compose up -d
   ```

3. Install other MCP servers (optional):
   ```bash
   npm install -g @modelcontextprotocol/server-github
   npm install -g @modelcontextprotocol/server-filesystem
   ```

---

## � Client Configurations

### [Cursor IDE](./cursor_settings.json)
Cursor supports MCP servers directly in its settings.

**Installation:**
1. Open Cursor Settings (`Ctrl/Cmd + ,`).
2. Search for "MCP" or open your `settings.json`.
3. Add the contents of `cursor_settings.json` to the `mcp.servers` object.
4. Reload the window.

### [Antigravity / Agentic Frameworks](./antigravity_config.json)
For configuring autonomous agents like Antigravity that support MCP.

**Usage:**
- Locate your agent's configuration file (often `agent_config.json` or `tools_config.json`).
- Insert the server definition from `antigravity_config.json`.
- The `autoAllow` field suggests tools the agent can run without explicit approval.

### [Gemini CLI / Generic YAML](./gemini_cli_config.yaml)
Many Python-based CLI tools and generic MCP clients use YAML for configuration.

**Usage:**
- Save as `mcp_config.yaml` in your project root or tool configuration directory.
- Pass the path to your CLI tool, e.g., `gemini-mcp --config mcp_config.yaml`.

---

## �🔧 Tool Availability by Configuration

| Tool | claude_desktop_config.json | claude_desktop_local.json |
|:-----|:---------------------------|:--------------------------|
| **Swarm Tools** | ✅ (via Docker) | ✅ (local Python) |
| `process_task()` | ✅ | ✅ |
| `search_codebase()` | ✅ | ✅ |
| `retrieve_context()` | ✅ | ✅ |
| `index_codebase()` | ✅ | ✅ |
| `get_status()` | ✅ | ✅ |
| **Docker Tools** | ✅ (via docker-mcp) | ❌ |
| `create_container()` | ✅ | ❌ |
| `run_command()` | ✅ | ❌ |
| **GitHub Tools** | ✅ (via github-mcp) | ❌ |
| `create_issue()` | ✅ | ❌ |
| `create_pr()` | ✅ | ❌ |
| **Filesystem Tools** | ✅ (via fs-mcp) | ❌ |
| `read_file()` | ✅ | ❌ |
| `write_file()` | ✅ | ❌ |

---

## 🎯 Recommended Configurations

### For Software Development
Use **`claude_desktop_config.json`** (multi-server) to get:
- Code search and refactoring (Swarm)
- Isolated testing (Docker)
- Version control (GitHub)
- Direct file access (Filesystem)

### For Testing Swarm
Use **`claude_desktop_local.json`** for:
- Quick iteration on Swarm features
- No Docker dependency
- Faster startup time
- Development mode

---

## 🔍 Verifying Installation

**Expected tools from Swarm:**
- `process_task`
- `get_status`
- `search_codebase`
- `index_codebase`
- `retrieve_context`

---

## 🐛 Troubleshooting

### Swarm tools not appearing
- Verify Docker container is running: `docker ps | grep swarm`
- Check container logs: `docker compose logs swarm-orchestrator`
- Ensure container name matches config: `swarm-mcp-server`

### "Command not found" errors
- Install FastMCP: `pip install fastmcp>=2.0.0`
- Verify Python in PATH
- Check working directory in config

### API key errors (search/indexing)
- Set environment variables before starting.
- Or add to Docker Compose `.env` file
- Test with: `docker exec swarm-mcp-server env | grep API_KEY`

---

## 📚 Additional Resources

- [Swarm Documentation](../../README.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Docker MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/docker)
