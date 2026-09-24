# MCP Quick Setup (VS Code Extensions)

## 1) Chrome DevTools MCP

1. Install the extension:
 <https://marketplace.visualstudio.com/items?itemName=VijayNirmal.chrome-devtools-mcp-relay>
2. Open Command Palette and run the MCP add/setup command.
3. Follow the VS Code wizard prompts to finish MCP registration.
4. Start a browser with remote debugging enabled (Chrome or Edge).
5. In Copilot Chat (Agent/Tools mode), verify DevTools MCP tools are available.

## 2) GitHub MCP

1. Install/enable GitHub Copilot:
<https://marketplace.visualstudio.com/items?itemName=GitHub.copilot>
2. Open Command Palette and run the MCP add/setup command.
3. Use the VS Code MCP wizard to add the GitHub MCP server.
4. Sign in to GitHub when prompted by VS Code.
5. In Copilot Chat (Agent/Tools mode), verify GitHub MCP tools are available.

## Note (DevTools fallback)

If DevTools MCP setup through VS Code does not work, use the files in `Archive` as fallback references (browser launch scripts, MCP examples, and troubleshooting notes).
