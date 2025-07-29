"""Configuration management for XL2TIMES MCP Server."""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the MCP server."""

    # Server settings
    SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "xl2times-mcp-server")
    SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "0.1.0")
    SERVER_DESCRIPTION: str = "MCP server for xl2times VEDA-TIMES processing"

    # XL2TIMES settings
    XL2TIMES_COMMAND: str = os.getenv("XL2TIMES_COMMAND", "uvx xl2times")
    XL2TIMES_TIMEOUT: int = int(os.getenv("XL2TIMES_TIMEOUT", "300"))

    # File handling
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/xl2times-mcp"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "xl2times-mcp.log")
    LOG_MAX_SIZE: str = os.getenv("LOG_MAX_SIZE", "10MB")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "7 days")

    # GAMS API settings (for Phase 2)
    GAMS_API_URL: Optional[str] = os.getenv("GAMS_API_URL")
    GAMS_API_KEY: Optional[str] = os.getenv("GAMS_API_KEY")

    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        # Create temp directory if it doesn't exist
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        # Log configuration
        logger.info(f"Server: {cls.SERVER_NAME} v{cls.SERVER_VERSION}")
        logger.info(f"XL2TIMES command: {cls.XL2TIMES_COMMAND}")
        logger.info(f"Temp directory: {cls.TEMP_DIR}")
        logger.info(f"Max file size: {cls.MAX_FILE_SIZE_MB}MB")

    @classmethod
    def setup_logging(cls) -> None:
        """Configure loguru logging."""
        logger.remove()  # Remove default handler

        # Console logging to stderr (to avoid interfering with MCP protocol on stdout)
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=cls.LOG_LEVEL,
            colorize=True
        )

        # File logging if configured
        if cls.LOG_FILE:
            logger.add(
                cls.LOG_FILE,
                rotation=cls.LOG_MAX_SIZE,
                retention=cls.LOG_RETENTION,
                level=cls.LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
            )


# Initialize configuration
config = Config()
