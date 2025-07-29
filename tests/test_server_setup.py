"""Tests for basic MCP server setup."""

import os
import sys
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.server import XL2TimesMCPServer


def test_config_defaults():
    """Test that configuration has correct defaults."""
    config = Config()

    assert config.SERVER_NAME == "xl2times-mcp-server"
    assert config.SERVER_VERSION == "0.1.0"
    assert config.XL2TIMES_COMMAND == "uvx xl2times"
    assert config.XL2TIMES_TIMEOUT == 300
    assert config.MAX_FILE_SIZE_MB == 100
    assert config.LOG_LEVEL == "INFO"


def test_config_from_env():
    """Test configuration from environment variables."""
    with patch.dict(os.environ, {
        "MCP_SERVER_NAME": "test-server",
        "XL2TIMES_TIMEOUT": "600",
        "MAX_FILE_SIZE_MB": "200"
    }):
        # Need to reload config module to pick up env changes
        from importlib import reload

        import src.config
        reload(src.config)
        config = src.config.Config()

        assert config.SERVER_NAME == "test-server"
        assert config.XL2TIMES_TIMEOUT == 600
        assert config.MAX_FILE_SIZE_MB == 200


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that MCP server initializes correctly."""
    server = XL2TimesMCPServer()

    assert server.server is not None
    assert server.xl2times_handler is not None
    assert server.info_handler is not None


@pytest.mark.asyncio
async def test_list_tools():
    """Test that server lists correct tools."""
    server = XL2TimesMCPServer()
    tools = await server._list_tools()

    assert len(tools) == 2

    tool_names = [tool.name for tool in tools]
    assert "xl2times_run" in tool_names
    assert "xl2times_info" in tool_names

    # Check xl2times_run tool schema
    xl2times_tool = next(t for t in tools if t.name == "xl2times_run")
    assert "input" in xl2times_tool.inputSchema["required"]
    assert "output_dir" in xl2times_tool.inputSchema["properties"]
    assert "regions" in xl2times_tool.inputSchema["properties"]


@pytest.mark.asyncio
async def test_call_tool_xl2times_info():
    """Test calling xl2times_info tool."""
    server = XL2TimesMCPServer()

    result = await server._call_tool("xl2times_info", {})

    assert len(result) == 1
    assert result[0].type == "text"

    # Parse the result text (should be JSON)
    import json
    info = json.loads(result[0].text)

    assert "server" in info
    assert "xl2times" in info
    assert "capabilities" in info
    assert info["server"]["name"] == "xl2times-mcp-server"


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool returns error."""
    server = XL2TimesMCPServer()

    result = await server._call_tool("unknown_tool", {})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "error" in result[0].text
    assert "TOOL_ERROR" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_xl2times_run_no_input():
    """Test xl2times_run fails without input."""
    server = XL2TimesMCPServer()

    result = await server._call_tool("xl2times_run", {})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "error" in result[0].text
