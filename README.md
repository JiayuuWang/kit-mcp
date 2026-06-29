# Kit (ConvertKit) MCP Server

Type 3 DAuth MCP server for the [Kit (ConvertKit)](https://kit.com) API.

## Tools

| Tool | Description |
|------|-------------|
| `list_forms` | List Forms |
| `list_sequences` | List Sequences |
| `list_subscribers` | List Subscribers |
| `get_subscriber` | Get Subscriber |
| `add_subscriber` | Add Subscriber |
| `tag_subscriber` | Tag Subscriber |

## Auth Setup (Personal API key (Bearer))

1. Go to **Kit → Settings → Developer → API Keys**
2. Copy the Personal API key

## Environment Variables

```bash
KIT_API_KEY=your_key
```

## Deploy

```bash
pip install -e .
python src/main.py
```

## Usage

```python
result = await runner.run(
    input="Show me kit data",
    mcp_servers=["JiayuWang/kit-mcp"],
)
```

## Safety Notes

- All read tools are safe for production
- Write tools are clearly marked with ⚠️ in their descriptions
