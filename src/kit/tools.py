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


@tool(description="Kit: list all landing page forms", annotations=ToolAnnotations(readOnlyHint=True))
async def kit_list_forms() -> Result:
    return await _req(HttpMethod.GET, "/forms")


@tool(description="Kit: list all email sequences", annotations=ToolAnnotations(readOnlyHint=True))
async def kit_list_sequences() -> Result:
    return await _req(HttpMethod.GET, "/sequences")


@tool(description="Kit: list subscribers with optional pagination", annotations=ToolAnnotations(readOnlyHint=True))
async def kit_list_subscribers(page: int = 1, limit: int = 50) -> Result:
    params = {"page": page, "limit": limit}
    return await _req(HttpMethod.GET, "/subscribers", params=params)


@tool(description="Kit: get a subscriber's details by ID or email", annotations=ToolAnnotations(readOnlyHint=True))
async def kit_get_subscriber(subscriber_id: Optional[int] = None, email: Optional[str] = None) -> Result:
    if subscriber_id:
        return await _req(HttpMethod.GET, f"/subscribers/{subscriber_id}")
    elif email:
        return await _req(HttpMethod.GET, "/subscribers", params={"email_address": email})
    return [TextContent(type="text", text=json.dumps({"error": "Must provide subscriber_id or email"}, indent=2))]


@tool(description="Kit: add a new subscriber to the account", annotations=ToolAnnotations(readOnlyHint=False))
async def kit_add_subscriber(email: str, first_name: Optional[str] = None, fields: Optional[str] = None) -> Result:
    body = {"email": email}
    if first_name:
        body["first_name"] = first_name
    if fields:
        body["fields"] = json.loads(fields)
    return await _req(HttpMethod.POST, "/subscribers", body=body)


@tool(description="Kit: add a tag to a subscriber", annotations=ToolAnnotations(readOnlyHint=False))
async def kit_tag_subscriber(subscriber_id: int, tag_id: int) -> Result:
    return await _req(HttpMethod.POST, f"/subscribers/{subscriber_id}/tags", body={"tag": {"id": tag_id}})


kit_tools = [
    kit_list_forms,
    kit_list_sequences,
    kit_list_subscribers,
    kit_get_subscriber,
    kit_add_subscriber,
    kit_tag_subscriber,
]

__all__ = ["kit", "kit_tools"]
