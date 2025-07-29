#!/usr/bin/env python3
"""
Test client for XL2TIMES MCP Server

Run from the project root with:
    uv run python examples/test_client/client.py
"""

import asyncio
import json
import os
from typing import Any, Dict

from pydantic import AnyUrl

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Create server parameters for stdio connection
env = dict(os.environ)
env["LOG_LEVEL"] = "DEBUG"  # Enable debug logging in the server
server_params = StdioServerParameters(
    command="uv",  # Using uv to run the server
    args=["run", "xl2times-mcp-server"],  # Run our MCP server
    env=env,
)


async def test_xl2times_server():
    """Test the XL2TIMES MCP server functionality."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("🚀 Connecting to XL2TIMES MCP Server...")
            
            # Initialize the connection
            await session.initialize()
            print("✅ Connected successfully!")
            
            # List available tools
            print("\n📋 Listing available tools...")
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test xl2times_info tool
            print("\n🔍 Testing xl2times_info tool...")
            try:
                result = await session.call_tool("xl2times_info", arguments={})
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        info = json.loads(content.text)
                        print("Server Info:")
                        print(f"  - Name: {info['server']['name']}")
                        print(f"  - Version: {info['server']['version']}")
                        print(f"  - Platform: {info['server']['platform']}")
                        print(f"  - XL2TIMES Available: {info['xl2times']['available']}")
                        print(f"  - XL2TIMES Command: {info['xl2times']['command']}")
            except Exception as e:
                print(f"❌ Error calling xl2times_info: {e}")
            
            # Test xl2times_run tool with missing input (should fail)
            print("\n🧪 Testing xl2times_run with missing input (should fail)...")
            try:
                result = await session.call_tool("xl2times_run", arguments={})
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        if 'error' in response:
                            print(f"✅ Expected error received: {response['error']['message']}")
                        else:
                            print(f"Response: {response}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
            
            # Test xl2times_run tool with sample input (placeholder response)
            print("\n🧪 Testing xl2times_run with sample input...")
            try:
                test_args = {
                    "input": "test_model.xlsx",
                    "output_dir": "output",
                    "regions": ["USA", "EUR"],
                    "verbose": 1
                }
                result = await session.call_tool("xl2times_run", arguments=test_args)
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        print(f"Response: {json.dumps(response, indent=2)}")
            except Exception as e:
                print(f"❌ Error calling xl2times_run: {e}")
            
            print("\n✨ Test completed!")


def main():
    """Entry point for the test client."""
    try:
        asyncio.run(test_xl2times_server())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()