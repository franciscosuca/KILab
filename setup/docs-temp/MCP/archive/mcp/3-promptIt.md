# Usage in VS Code Copilot

Once configured, you can use Copilot Chat to interact with your local website.

1. Open the **Copilot Chat** panel in VS Code.
2. Ensure the "Agent" or "Tools" mode is active (usually by typing `@` or looking for the tool icon).
3. You can now ask questions like:
   * *"Analyze the console errors on my local site."*
   * *"Take a screenshot of the current page in Edge."*
   * *"What are the network requests failing on this page?"*

## Advanced Prompting for Deeper Web Analysis

Use ONLY `chrome-devtools-mcp` (not the integrated browser).

### Base Workflow (always include)

1. `list_pages` and `select_page` for URL `<https://localhost:[PORT]/[endpoint]>`
2. `navigate_page` with `type=reload` and `ignoreCache=true`
3. `list_console_messages` with `includePreservedMessages=true`
4. `list_network_requests` with `includePreservedRequests=true`
5. For each failed request (`status >= 400`), call `get_network_request`

### What to Ask the Agent to Report

* Console issue details: message, level, source file, line/column, stack trace (if available)
* Network issue details: URL, method, status, initiator/resource type, timing, and response preview
* Correlation: which console errors map to which failed requests
* Severity: `critical`, `high`, `medium`, `low` based on user impact
* Root-cause hypothesis for each issue
* Fastest fix and safer long-term fix

### Copy/Paste Prompt Template (Full Diagnostic)

```text
Use ONLY chrome-devtools-mcp (not integrated browser).

Target: https://localhost:[PORT]/[endpoint]

Run this exact flow:
1) list_pages and select_page for the target URL
2) navigate_page type=reload ignoreCache=true
3) list_console_messages includePreservedMessages=true
4) list_network_requests includePreservedRequests=true
5) For every request with status >= 400, call get_network_request

Analyze and return:
- A table of all console errors/warnings and failed network requests
- For each item: URL/file, method, status, resource type, concise error summary
- Likely root cause and confidence (high/medium/low)
- Exact fix recommendation (code/config level)
- Impact if ignored

Then provide:
1) Top 3 issues to fix first (ordered by user impact)
2) Quick wins (< 15 min)
3) Verification steps after applying fixes

If nothing is found, say exactly: "No console/network errors found after reload."
```

### Copy/Paste Prompt Template (API-Focused)

```text
Use ONLY chrome-devtools-mcp. Inspect https://localhost:[PORT]/api-heavy-page.

Reload with cache disabled, list all network requests, and deep inspect failures.
Focus on:
- 4xx/5xx patterns by endpoint
- CORS/auth/CSRF failures
- Slow requests (> 1000 ms)
- Payload or response shape mismatches (if visible)

Return:
1) Endpoint health summary table
2) Most likely backend vs frontend ownership per failure
3) Suggested retry, timeout, and error-handling improvements
```

### Copy/Paste Prompt Template (Frontend Stability)

```text
Use ONLY chrome-devtools-mcp. Inspect https://localhost:[PORT]/[endpoint].

After reload, analyze console + network and prioritize frontend runtime stability.
Check for:
- Unhandled promise rejections
- Module/chunk load failures
- Source map and MIME type issues
- Third-party script failures

Return a prioritized bug list with:
- Reproduction hints
- Suspected component/module
- Proposed patch direction
- Risk of regression
```

### Persistent Session Requirement

When diagnosing a page, keep all MCP actions in one continuous session. Do not restart the inspector between steps.

Why this matters:

* Preserves console and network context from the same reload event
* Keeps request IDs valid so `get_network_request` can resolve failed calls reliably
* Avoids false negatives caused by losing preserved messages/requests after reconnecting

Use this instruction in your prompt:

```text
Run all MCP steps in one persistent session (do not restart inspector between steps):
select_page -> reload -> list_console_messages -> list_network_requests -> get_network_request for failed request IDs.

If the MCP session resets, restart the flow from select_page and report that the previous context was discarded.
```
