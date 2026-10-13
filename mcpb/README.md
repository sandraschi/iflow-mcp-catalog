# iflow-mcp-catalog (MCPB Bundle)

FastMCP 3.1.0 catalog: GitHub org MCP fork index (iflow-mcp) with SOTA webapp

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "iflow-mcp-catalog": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "iflow_mcp_catalog"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **iflow_catalog_refresh**: iflow_catalog_refresh

## Requirements

- Python 3.12+
- uv
