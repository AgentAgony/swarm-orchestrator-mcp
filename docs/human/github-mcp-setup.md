# GitHub MCP Integration Setup

This guide explains how to enable GitHub operations for the Swarm autonomous worker team.

---

## Prerequisites

- Docker Desktop installed
- GitHub Personal Access Token (PAT) with `repo` scope
- Swarm MCP server running in Docker

---

## Step 1: Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Set scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Click **Generate token**
5. **Copy the token** (you won't see it again!)

---

## Step 2: Set Environment Variable

### Windows (PowerShell)
```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'your-token-here', 'User')
```

### Linux/macOS
```bash
export GITHUB_TOKEN="your-token-here"
# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export GITHUB_TOKEN="your-token-here"' >> ~/.bashrc
```

---

## Step 3: Update MCP Configuration

Add GitHub MCP server to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "swarm-orchestrator": { ... },
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Or use Docker Desktop MCP Toolkit**:
1. Open Docker Desktop → Extensions → MCP Toolkit
2. Click "Add Server" → Select "GitHub"
3. Enter your `GITHUB_TOKEN`

---

## Step 4: Verify Integration

Test that GitHub MCP is accessible:

```bash
# Test GitHub MCP connection
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_TOKEN \
  mcp/github
```

Expected: GitHub MCP server starts and shows available tools.

---

## Available Tools

The GitHub MCP server provides:

| Tool | Description | Swarm Worker |
|------|-------------|--------------|
| `push_files` | Push multiple files in one commit | CommitWorker |
| `create_pull_request` | Create a new PR | PRWorker |
| `get_pull_request` | Get PR details and comments | ReviewWorker |
| `create_or_update_file` | Create/update single file | CommitWorker |
| `search_repositories` | Search GitHub repos | (future) |
| `create_issue` | Create issue from bug | (future) |

---

## Security Notes

⚠️ **Important**:
- Never commit `GITHUB_TOKEN` to version control
- Use environment variables or secret managers
- Tokens grant access to your repos—treat like passwords
- Rotate tokens periodically

---

## Troubleshooting

**Error: "GITHUB_PERSONAL_ACCESS_TOKEN not set"**
- Verify env var: `echo $GITHUB_TOKEN` (Linux/macOS) or `$env:GITHUB_TOKEN` (Windows)
- Restart terminal/IDE after setting

**Error: "403 Forbidden"**
- Token may lack required scopes
- Regenerate token with `repo` scope

**Error: "Docker container not found"**
- Pull image: `docker pull mcp/github`
- Check Docker Desktop is running
