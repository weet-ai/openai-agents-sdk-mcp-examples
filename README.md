# openai-agents-sdk-mcp-examples

Simple repository containing examples of how to use the OpenAI Agents SDK with custom Model Context Protocol servers (MCP).

## Prerequisites

- Python 3.13
- uv
- OpenAI Key
- [playwright](https://playwright.dev/python/docs/intro) (for browser automation example) & Chromium

## Getting started

- Install dependencies

```bash
uv sync
```

- Install Chromium via Playwright

```bash
uv run playwright install chromium
```

- Set your OpenAI API key as an environment variable

- For **stdio**:

```bash
uv run python src/agent_stdio.py
```

- For **streamable HTTP**:

```bash
uv run fastmcp run src/server.py && \
uv run python src/agent_streamable_http.py
```

