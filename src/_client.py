# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the Kit MCP server.

Required environment variables:
    DEDALUS_API_KEY  dsk-live-...
    KIT_API_KEY     Kit personal API key

Optional:
    MCP_SERVER_SLUG   default: JiayuWang/kit-mcp

Usage:
    python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from kit import kit  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL  = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
KIT_API_KEY = os.getenv("KIT_API_KEY", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang/kit-mcp")
MODEL           = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

REQUIRED_TOOLS = ["list_forms", "list_sequences", "list_subscribers", "get_subscriber", "add_subscriber", "tag_subscriber"]


def _passed(tool_name: str, tool_events: list) -> bool:
    if not tool_events:
        return False
    for event in tool_events:
        if hasattr(event, "name") and tool_name in event.name:
            return True
        if isinstance(event, dict) and tool_name in event.get("name", ""):
            return True
    return False


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    tool_events = []

    def on_tool_event(event):
        tool_events.append(event)

    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=4,
            max_tokens=2000,
            on_tool_event=on_tool_event,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:400])
        ok = _passed(tool_name, tool_events)
        if ok:
            print(f"✓ Tool called: {len(tool_events)} invocation(s)")
    except Exception as exc:
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set"); return 1
    if not KIT_API_KEY:
        print("Error: KIT_API_KEY not set"); return 1
    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    creds = [SecretValues(_rebind(kit, MCP_SERVER_SLUG), token=KIT_API_KEY)]
    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=DEDALUS_API_URL, as_base_url=DEDALUS_AS_URL)
    runner = DedalusRunner(client)

    print(f"Testing Kit MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    results["list_forms"] = await _run_tool(runner, creds, "list_forms",
        "Call list_forms and show each form id and name.")
    results["list_sequences"] = await _run_tool(runner, creds, "list_sequences",
        "Call list_sequences and show sequence names.")
    results["list_subscribers"] = await _run_tool(runner, creds, "list_subscribers",
        "Call list_subscribers with limit=5.")
    results["get_subscriber"] = await _run_tool(runner, creds, "get_subscriber",
        "Call list_subscribers, take the first subscriber's id, then call get_subscriber on it.")
    results["add_subscriber"] = await _run_tool(runner, creds, "add_subscriber",
        "Call add_subscriber with email='dedalus-smoke-test@example.com' and first_name='Dedalus'.")
    results["tag_subscriber"] = await _run_tool(runner, creds, "tag_subscriber",
        "Call list_subscribers to get a subscriber id, then tag_subscriber with that id and tag_id=1.")

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
