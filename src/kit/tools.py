"""Kit (ConvertKit) MCP tools - Type 3 DAuth implementation."""

import json
from typing import Optional

from mcp.types import TextContent
from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations

_BASE_URL = "https://api.kit.com/v4"

kit = Connection(
    name="JiayuWang-kit-mcp",
    secrets=SecretKeys(token="KIT_API_KEY"),
    base_url=_BASE_URL,
    auth_header_format="Bearer {api_key}",
)

Result = list[TextContent]


async def _req(method: HttpMethod, path: str, body: dict | None = None, params: dict | None = None) -> Result:
    ctx = get_context()
    resp = await ctx.dispatch(
        "JiayuWang-kit-mcp",
        HttpRequest(method=method, path=path, body=body, params=params),
    )
    if resp.success:
        return [TextContent(type="text", text=json.dumps(resp.response.body or {}, indent=2))]
    error = resp.error.message if resp.error else "Request failed"
    return [TextContent(type="text", text=json.dumps({"error": error}, indent=2))]


@tool(description="List all forms in the Kit account", annotations=ToolAnnotations(readOnlyHint=True))
async def list_forms() -> Result:
    """List all landing page forms with their IDs and names."""
    return await _req(HttpMethod.GET, "/forms")


@tool(description="List all email sequences", annotations=ToolAnnotations(readOnlyHint=True))
async def list_sequences() -> Result:
    """List all sequences (automated email courses) with their IDs and subscriber counts."""
    return await _req(HttpMethod.GET, "/sequences")


@tool(description="List subscribers with optional pagination", annotations=ToolAnnotations(readOnlyHint=True))
async def list_subscribers(page: int = 1, limit: int = 50) -> Result:
    """List subscribers.
    
    Args:
        page: Page number (default 1)
        limit: Results per page (default 50)
    """
    params = {"page": page, "limit": limit}
    return await _req(HttpMethod.GET, "/subscribers", params=params)


@tool(description="Get a subscriber's details by ID or email", annotations=ToolAnnotations(readOnlyHint=True))
async def get_subscriber(subscriber_id: Optional[int] = None, email: Optional[str] = None) -> Result:
    """Get subscriber profile.
    
    Args:
        subscriber_id: Subscriber ID
        email: Email address (alternative to ID)
    """
    if subscriber_id:
        return await _req(HttpMethod.GET, f"/subscribers/{subscriber_id}")
    elif email:
        params = {"email_address": email}
        return await _req(HttpMethod.GET, "/subscribers", params=params)
    return [TextContent(type="text", text=json.dumps({"error": "Must provide subscriber_id or email"}, indent=2))]


@tool(description="Add a new subscriber to the account", annotations=ToolAnnotations(readOnlyHint=False))
async def add_subscriber(email: str, first_name: Optional[str] = None, fields: Optional[str] = None) -> Result:
    """Subscribe a new email address.
    
    Args:
        email: Email address
        first_name: Optional first name
        fields: Optional custom fields as JSON object
    """
    body = {"email": email}
    if first_name:
        body["first_name"] = first_name
    if fields:
        body["fields"] = json.loads(fields)
    return await _req(HttpMethod.POST, "/subscribers", body=body)


@tool(description="Add a tag to a subscriber", annotations=ToolAnnotations(readOnlyHint=False))
async def tag_subscriber(subscriber_id: int, tag_id: int) -> Result:
    """Tag a subscriber.
    
    Args:
        subscriber_id: Subscriber ID
        tag_id: Tag ID to apply
    """
    body = {"tag": {"id": tag_id}}
    return await _req(HttpMethod.POST, f"/subscribers/{subscriber_id}/tags", body=body)


kit_tools = [
    list_forms,
    list_sequences,
    list_subscribers,
    get_subscriber,
    add_subscriber,
    tag_subscriber,
]

__all__ = ["kit", "kit_tools"]
