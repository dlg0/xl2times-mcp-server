"""Main MCP server implementation for XL2TIMES."""

import asyncio
import json
import sys
from typing import Any, Dict, List

from loguru import logger
from mcp.server import Server
import mcp.server.stdio
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool, ServerCapabilities, ToolsCapability
from mcp.server.lowlevel.server import InitializationOptions

from .config import config
from .handlers.info_handler import InfoHandler
from .handlers.xl2times_handler import XL2TimesHandler


class XL2TimesMCPServer:
    """Main MCP server for XL2TIMES operations."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server(config.SERVER_NAME)
        self.xl2times_handler = XL2TimesHandler()
        self.info_handler = InfoHandler()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all MCP handlers."""
        # Register tool handlers
        self.server.list_tools()(self._list_tools)
        self.server.call_tool()(self._call_tool)

        logger.info("All handlers registered successfully")

    async def _list_tools(self) -> List[Tool]:
        """List available tools."""
        tools = [
            Tool(
                name="xl2times_run",
                description="Run xl2times with specified input files and options",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": ["string", "array"],
                            "description": "Input directory or list of xlsx/xlsm files",
                            "items": {"type": "string"} if isinstance([], list) else None
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated files"
                        },
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of regions to include"
                        },
                        "include_dummy_imports": {
                            "type": "boolean",
                            "description": "Include dummy import processes",
                            "default": False
                        },
                        "ground_truth_dir": {
                            "type": "string",
                            "description": "Ground truth directory for comparison"
                        },
                        "dd": {
                            "type": "boolean",
                            "description": "Output DD files",
                            "default": False
                        },
                        "only_read": {
                            "type": "boolean",
                            "description": "Only read files and output raw_tables.txt",
                            "default": False
                        },
                        "no_cache": {
                            "type": "boolean",
                            "description": "Ignore cache and re-extract from XLSX",
                            "default": False
                        },
                        "verbose": {
                            "type": "integer",
                            "description": "Verbosity level (0-4)",
                            "default": 0,
                            "minimum": 0,
                            "maximum": 4
                        }
                    },
                    "required": ["input"]
                }
            ),
            Tool(
                name="xl2times_info",
                description="Get information about xl2times installation and server capabilities",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

        logger.debug(f"Listing {len(tools)} tools")
        return tools

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls."""
        logger.info(f"Tool called: {name} with arguments: {arguments}")

        try:
            if name == "xl2times_run":
                result = await self.xl2times_handler.run(arguments)
            elif name == "xl2times_info":
                result = await self.info_handler.get_info()
            else:
                raise ValueError(f"Unknown tool: {name}")

            # Convert result to JSON string if it's a dict
            if isinstance(result, dict):
                result_text = json.dumps(result, indent=2)
            else:
                result_text = str(result)
            
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            logger.error(f"Error in tool {name}: {str(e)}")
            error_result = {
                "error": {
                    "code": "TOOL_ERROR",
                    "message": str(e),
                    "tool": name
                }
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

def create_server() -> Server:
    """Create and configure the MCP server."""
    # Setup configuration and logging
    config.setup_logging()
    config.validate()
    
    logger.info(f"Creating {config.SERVER_NAME} v{config.SERVER_VERSION}")
    
    # Create and configure the server instance
    server_instance = XL2TimesMCPServer()
    return server_instance.server


async def run_server():
    """Run the MCP server."""
    server = create_server()
    
    # Use stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION} on stdio...")
        
        initialization_options = InitializationOptions(
            server_name=config.SERVER_NAME,
            server_version=config.SERVER_VERSION,
            capabilities=ServerCapabilities(
                tools=ToolsCapability()
            )
        )
        
        await server.run(
            read_stream=read_stream,
            write_stream=write_stream, 
            initialization_options=initialization_options
        )


def main():
    """Main entry point."""
    try:
        # Run the async server
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

