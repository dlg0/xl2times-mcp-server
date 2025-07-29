# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-07-29-core-mcp-server/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Technical Requirements

- **MCP Protocol Implementation**: Use python-sdk to implement the Model Context Protocol server with proper request/response handling
- **Command Wrapper Architecture**: Design a modular wrapper system that maps MCP requests to xl2times CLI commands with argument validation
- **File I/O Management**: Implement secure temporary file handling for Excel inputs and GAMS outputs with automatic cleanup
- **Process Execution**: Use Python subprocess module to safely execute xl2times commands with timeout and resource limits
- **Error Parsing**: Create parsers for xl2times output to extract error messages, warnings, and validation results
- **Async Support**: Implement async request handling for long-running xl2times operations
- **Configuration Loading**: Use python-dotenv to load environment variables for API keys, file paths, and server settings
- **Structured Logging**: Implement loguru with appropriate log levels, rotation, and formatting for debugging

## Approach Options

**Option A: Direct CLI Wrapper** (Selected)
- Pros: Simple implementation, direct mapping to xl2times commands, no API dependencies
- Cons: Need to parse text outputs, process management complexity

**Option B: Python API Integration**
- Pros: Would provide better control over execution if available
- Cons: xl2times is primarily a CLI tool, no documented Python API

**Rationale:** Option A is the only viable approach since xl2times is distributed as a CLI tool via uvx. We'll implement robust output parsing and process management to handle the CLI interaction effectively.

## External Dependencies

- **python-sdk** - Official MCP Python SDK for protocol implementation
- **Justification:** Required for MCP server functionality

- **xl2times** - Core library for VEDA-TIMES conversion
- **Justification:** Primary functionality being exposed through MCP

- **python-dotenv** - Environment variable management
- **Justification:** Secure configuration management for API keys and settings

- **loguru** - Advanced Python logging
- **Justification:** Better logging capabilities than standard library, essential for debugging MCP interactions

- **fastapi** - Modern Python web framework (for future GAMS API)
- **Justification:** Will be needed in Phase 2, including now for consistency

## Architecture Design

### Server Structure
```
xl2times-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server entry point
│   ├── handlers/          # MCP request handlers
│   │   ├── __init__.py
│   │   ├── xl2times_handler.py  # Main xl2times run handler
│   │   └── info_handler.py       # Server info handler
│   ├── wrappers/          # xl2times command wrappers
│   │   ├── __init__.py
│   │   └── xl2times.py    # Core wrapper implementation
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── file_manager.py
│   │   └── error_parser.py
│   └── config.py          # Configuration management
├── tests/
├── .env.example
└── pyproject.toml
```

### Request Flow
1. LLM sends MCP request (e.g., "convert VEDA model")
2. Server routes to appropriate handler
3. Handler validates request parameters
4. Wrapper executes xl2times with proper arguments
5. Output is parsed and structured
6. Response sent back through MCP protocol

### Error Handling Strategy
- Wrap all xl2times calls in try/except blocks
- Parse stderr and stdout for error patterns
- Transform errors into structured JSON with:
  - Error type (validation, file not found, syntax, etc.)
  - File location
  - Line/column numbers where applicable
  - Suggested fixes when possible
  - Original error message for reference