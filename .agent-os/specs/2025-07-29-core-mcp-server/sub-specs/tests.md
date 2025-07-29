# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-07-29-core-mcp-server/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Test Coverage

### Unit Tests

**XL2TimesWrapper**
- Test command construction for convert, validate, extract operations
- Test parameter validation and sanitization
- Test error handling for missing xl2times installation
- Test output parsing for different xl2times responses
- Test timeout handling for long-running operations

**FileManager**
- Test temporary file creation and cleanup
- Test file path validation and security checks
- Test handling of large files and memory constraints
- Test concurrent file access handling
- Test automatic cleanup on process termination

**ErrorParser**
- Test parsing of xl2times validation errors
- Test extraction of line/column information
- Test categorization of error types
- Test generation of user-friendly error messages
- Test handling of malformed error outputs

**ConfigManager**
- Test loading of environment variables
- Test default value handling
- Test configuration validation
- Test secure handling of API keys
- Test configuration reload functionality

### Integration Tests

**MCP Server Initialization**
- Test server startup with valid configuration
- Test tool registration and schema validation
- Test graceful shutdown handling
- Test port binding and release
- Test logging initialization

**Convert Command Flow**
- Test end-to-end conversion of sample VEDA file
- Test handling of invalid Excel files
- Test output file generation and structure
- Test concurrent conversion requests
- Test memory usage during large file processing

**Validate Command Flow**
- Test validation of correct VEDA files
- Test detailed error reporting for invalid files
- Test performance with large Excel files
- Test handling of corrupted files
- Test validation timeout scenarios

**Error Response Flow**
- Test structured error response generation
- Test error logging and tracking
- Test client-friendly error messages
- Test error recovery mechanisms
- Test rate limiting error responses

### Feature Tests

**LLM Agent Workflow**
- Test complete workflow: connect → validate → convert → disconnect
- Test handling of multiple sequential operations
- Test error recovery and retry logic
- Test session management across requests
- Test resource cleanup after agent disconnection

**File Processing Pipeline**
- Test upload → process → download flow
- Test handling of multiple file formats
- Test progress reporting for long operations
- Test cancellation of in-progress operations
- Test result caching for repeated requests

### Mocking Requirements

- **xl2times CLI:** Mock subprocess calls to xl2times for unit tests, use real xl2times for integration tests
- **File System:** Mock file operations for unit tests, use temp directories for integration tests
- **Environment Variables:** Mock os.environ for configuration tests
- **Time-based Operations:** Mock time.time() for timeout tests
- **Random Values:** Mock uuid generation for consistent request IDs in tests

## Test Data

### Sample Files
- `valid_model.xlsx`: Valid VEDA-TIMES model for happy path tests
- `invalid_syntax.xlsx`: Model with known syntax errors for validation tests
- `large_model.xlsx`: Large file for performance tests
- `corrupted.xlsx`: Corrupted Excel file for error handling tests
- `empty.xlsx`: Empty Excel file for edge case tests

### Expected Outputs
- Pre-generated GAMS output files for comparison
- Known error messages for validation tests
- Performance benchmarks for regression testing

## Test Environment

### Dependencies
- pytest: Test framework
- pytest-asyncio: Async test support
- pytest-mock: Mocking functionality
- pytest-cov: Coverage reporting
- hypothesis: Property-based testing for input validation

### Configuration
- Test-specific `.env.test` file
- Isolated temp directories per test
- Configurable timeouts for CI/CD environments

## Coverage Goals

- Unit test coverage: 90%
- Integration test coverage: 80%
- Critical path coverage: 100%
- Error handling coverage: 100%