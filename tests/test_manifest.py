import asyncio
import json

from approvaltests import verify

from racn_mcp.server import mcp


def test_tools_manifest():
    """The JSON manifest a consuming MCP client reads via `tools/list`."""
    tools = asyncio.run(mcp.list_tools())
    manifest = [tool.model_dump(mode="json", exclude_none=True) for tool in tools]

    verify(json.dumps(manifest, indent=2))
