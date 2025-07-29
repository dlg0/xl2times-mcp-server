# Technical Stack

> Last Updated: 2025-07-29
> Version: 1.0.0

## Core Technologies

- **Application Framework:** Python 3.13+
- **Package Manager:** uv
- **MCP SDK:** python-sdk (official MCP Python SDK)
- **API Framework:** FastAPI (for GAMS API server)
- **Configuration Management:** python-dotenv
- **Logging:** loguru

## Development Tools

- **Project Management:** uv (for dependency management and packaging)
- **Distribution:** PyPI (via uvx command)
- **Testing Framework:** pytest
- **Code Quality:** ruff (linting and formatting)

## External Dependencies

- **xl2times:** Core library for VEDA-TIMES conversion (via uvx)
- **GAMS:** External GAMS solver (accessed via API)

## Infrastructure

- **Database System:** n/a (file-based operations)
- **JavaScript Framework:** n/a
- **Import Strategy:** n/a
- **CSS Framework:** n/a
- **UI Component Library:** n/a
- **Fonts Provider:** n/a
- **Icon Library:** n/a

## Deployment

- **Application Hosting:** Local execution via uvx
- **Database Hosting:** n/a
- **Asset Hosting:** n/a
- **Deployment Solution:** PyPI package distribution
- **Code Repository URL:** https://github.com/[USERNAME]/xl2times-mcp-server (TBD)

## CI/CD

- **Platform:** GitHub Actions
- **Trigger:** Push to main/staging branches
- **Tests:** Run before deployment
- **Package Publishing:** Automated to PyPI on release tags