import asyncio

from approvaltests import verify_as_json

from racn_mcp.server import mcp


def test_tools_manifest():
    """The JSON manifest a consuming MCP client reads via `tools/list`."""
    tools = asyncio.run(mcp.list_tools())
    manifest = [tool.model_dump(mode="json", exclude_none=True) for tool in tools]

    verify_as_json(manifest)
