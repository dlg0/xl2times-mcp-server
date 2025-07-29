# XL2TIMES MCP Server Examples

This directory contains examples for using the XL2TIMES MCP Server.

## Test Client

The `test_client` directory contains a simple MCP client that tests the basic functionality of the XL2TIMES MCP Server.

### Running the Test Client

From the project root directory, run:

```bash
uv run python examples/test_client/client.py
```

The test client will:
1. Connect to the XL2TIMES MCP Server
2. List available tools
3. Test the `xl2times_info` tool to get server information
4. Test the `xl2times_run` tool with missing input (expecting an error)
5. Test the `xl2times_run` tool with sample input

### What to Expect

The test client demonstrates:
- How to establish a connection to the MCP server
- How to discover available tools
- How to call tools with arguments
- How to handle responses and errors

This is useful for:
- Verifying the server is working correctly
- Understanding the MCP protocol interaction
- Testing new features as they're developed