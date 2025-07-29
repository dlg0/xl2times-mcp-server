# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-07-29-core-mcp-server/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## MCP Protocol Endpoints

### Tool: xl2times_run

**Purpose:** Run xl2times with specified input files and options
**Parameters:**
- `input`: string | [string] (required) - Either an input directory or list of xlsx/xlsm files
- `output_dir`: string (optional) - Output directory for generated files
- `regions`: [string] (optional) - Comma-separated list of regions to include
- `include_dummy_imports`: boolean (optional, default: false) - Include dummy import processes
- `ground_truth_dir`: string (optional) - Ground truth directory for comparison
- `dd`: boolean (optional, default: false) - Output DD files
- `only_read`: boolean (optional, default: false) - Only read files and output raw_tables.txt
- `no_cache`: boolean (optional, default: false) - Ignore cache and re-extract from XLSX
- `verbose`: number (optional, default: 0) - Verbosity level (0-4)

**Response:**
```json
{
  "success": boolean,
  "output_files": [string],
  "output_directory": string,
  "logs": string,
  "warnings": [string],
  "errors": [string],
  "raw_tables": object | null,
  "execution_time": number
}
```

**Errors:**
- `NO_INPUT`: No input files or directory provided
- `FILE_NOT_FOUND`: Input file or directory doesn't exist
- `INVALID_FORMAT`: File is not a valid xlsx/xlsm file
- `CONVERSION_ERROR`: xl2times processing failed
- `PERMISSION_ERROR`: Cannot write to output directory

### Tool: xl2times_info

**Purpose:** Get information about xl2times installation and capabilities
**Parameters:** None

**Response:**
```json
{
  "version": string,
  "supported_formats": [string],
  "available_commands": [string],
  "configuration": {
    "temp_dir": string,
    "max_file_size": number,
    "timeout": number
  }
}
```

## MCP Server Configuration

### Server Initialization
```python
# MCP server configuration
server = MCPServer(
    name="xl2times-mcp-server",
    version="1.0.0",
    description="MCP server for xl2times VEDA-TIMES processing"
)
```

### Tool Registration
All tools are registered with the MCP server on startup with proper parameter schemas and descriptions for LLM understanding.

## Error Response Format

All errors follow a consistent structure:
```json
{
  "error": {
    "code": string,
    "message": string,
    "details": object | null,
    "timestamp": string,
    "request_id": string
  }
}
```

## Rate Limiting and Timeouts

- Default timeout: 300 seconds for conversion operations
- Default timeout: 60 seconds for validation operations
- Maximum file size: 100MB for Excel files
- Concurrent request limit: 10 per client