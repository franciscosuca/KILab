# Chome DevTools MCP Server

To set this up so your VS Code Copilot (or other local agents) can inspect your local development sites in Edge, follow these steps:

## 1. Launch browser in Remote Debugging Mode

See [Launch Browser Setup](./1-launchBrowser.md) for the browser start script and troubleshooting steps.

## 2. Configure the MCP Server for Edge

You need to tell the MCP server to look for Edge instead of Chrome. You can do this by passing the path to the Edge executable via the `--executablePath` argument.

## 3. In VS Code (using the native MCP support)

VS Code recently added native support for MCP servers. You can configure this globally so Copilot Chat can access it.

1. Open VS Code.
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac) and search for **"MCP: Open User Configuration"**.
3. Add the following configuration to your `mcp.json` file:

If you prefer to let the MCP server connect to the Edge instance you already opened in Step 1, use the `--autoConnect` flag:

```json
{
  "mcpServers": {
    "edge-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp",
        "--autoConnect"
      ]
    }
  }
}
```
