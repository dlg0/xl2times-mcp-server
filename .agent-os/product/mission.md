# Product Mission

> Last Updated: 2025-07-29
> Version: 1.0.0

## Pitch

XL2TIMES MCP Server is a Model Context Protocol server that enables LLM agents to interact with VEDA-TIMES energy system models by exposing xl2times functionality and providing GAMS execution capabilities through an integrated API server.

## Users

### Primary Customers

- **Energy System Researchers**: Scientists and analysts building decarbonization pathway models using VEDA-TIMES
- **AI/LLM Application Developers**: Engineers integrating energy system modeling capabilities into AI-powered research tools

### User Personas

**Energy System Modeler** (25-55 years old)
- **Role:** Research Scientist or Energy Analyst
- **Context:** Working on national or regional decarbonization studies using TIMES models
- **Pain Points:** Manual VEDA-TIMES file processing is time-consuming, Difficulty automating model runs and analysis workflows
- **Goals:** Automate model validation and execution, Integrate modeling into larger research pipelines

**AI Research Engineer** (28-45 years old)
- **Role:** Software Engineer or ML Engineer
- **Context:** Building AI agents for climate and energy research applications
- **Pain Points:** Lack of programmatic access to energy system modeling tools, Complex integration with specialized modeling software
- **Goals:** Enable LLMs to understand and manipulate energy models, Create automated research workflows

## The Problem

### Manual VEDA-TIMES Workflow Complexity

Researchers spend significant time manually processing Excel files, checking for syntax errors, and running GAMS models through disconnected tools. This manual workflow can take hours per model iteration.

**Our Solution:** Provide unified programmatic access to xl2times functionality and GAMS execution through MCP.

### Limited AI Integration for Energy Modeling

Current energy system modeling tools lack interfaces for AI agents, preventing automation of model design, validation, and analysis workflows. Researchers cannot leverage LLMs to accelerate their modeling work.

**Our Solution:** Create an MCP server that exposes all xl2times capabilities to LLMs with integrated GAMS execution.

### Fragmented Toolchain

The VEDA-TIMES to GAMS workflow involves multiple disconnected tools and manual file transfers. Each step requires manual intervention and introduces potential for errors.

**Our Solution:** Integrate xl2times processing and GAMS API submission in a single, automated pipeline.

## Differentiators

### First MCP-Native Energy Modeling Interface

Unlike traditional CLI tools or Python libraries, we provide native MCP integration designed specifically for LLM interaction. This results in seamless AI-powered energy system modeling workflows.

### Integrated GAMS Execution Pipeline

Unlike separate xl2times and GAMS tools, we provide end-to-end model processing and execution. This results in 10x faster iteration cycles for model development.

## Key Features

### Core Features

- **XL2TIMES CLI Exposure:** Complete access to all xl2times commands through MCP protocol
- **VEDA Table Extraction:** Extract and analyze all VEDA tables from TIMES models
- **Syntax Validation:** Check VEDA table syntax and report errors with detailed diagnostics
- **GAMS File Generation:** Convert VEDA-TIMES Excel files to GAMS format automatically
- **GAMS API Integration:** Submit generated GAMS files to API server for execution

### Collaboration Features

- **Structured Error Reporting:** Provide LLM-friendly error messages and validation results
- **Progress Tracking:** Real-time status updates for long-running operations
- **File Management:** Handle model file organization and versioning
- **Configuration Management:** Support for environment-based API keys and server endpoints
- **Comprehensive Logging:** Detailed operation logs for debugging and audit trails