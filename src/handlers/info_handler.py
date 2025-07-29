"""Handler for xl2times_info tool."""

import platform
import subprocess
from typing import Any, Dict, Optional

from loguru import logger

from ..config import config


class InfoHandler:
    """Handler for server and xl2times information."""

    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about xl2times installation and server capabilities.

        Returns:
            Dictionary with server and xl2times information
        """
        logger.info("Processing xl2times_info request")

        # Get xl2times version
        xl2times_version = await self._get_xl2times_version()

        # Build info response
        info = {
            "server": {
                "name": config.SERVER_NAME,
                "version": config.SERVER_VERSION,
                "description": config.SERVER_DESCRIPTION,
                "platform": platform.platform(),
                "python_version": platform.python_version()
            },
            "xl2times": {
                "command": config.XL2TIMES_COMMAND,
                "version": xl2times_version,
                "timeout": config.XL2TIMES_TIMEOUT,
                "available": xl2times_version is not None
            },
            "capabilities": {
                "supported_formats": ["xlsx", "xlsm"],
                "max_file_size_mb": config.MAX_FILE_SIZE_MB,
                "temp_directory": str(config.TEMP_DIR),
                "available_options": [
                    "regions",
                    "include_dummy_imports",
                    "ground_truth_dir",
                    "dd",
                    "only_read",
                    "no_cache",
                    "verbose"
                ]
            }
        }

        logger.info("xl2times_info completed")
        return info

    async def _get_xl2times_version(self) -> Optional[str]:
        """Get xl2times version by running --help command."""
        try:
            # Try to get version from xl2times
            cmd = f"{config.XL2TIMES_COMMAND} --help"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse version from output if available
            # For now, just check if command works
            if result.returncode == 0:
                return "Available (version detection pending)"
            else:
                return None

        except Exception as e:
            logger.warning(f"Could not get xl2times version: {e}")
            return None

