"""Handler for xl2times_run tool."""

import time
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from ..wrappers.xl2times_wrapper import XL2TimesWrapper, XL2TimesError


class XL2TimesHandler:
    """Handler for xl2times operations."""

    def __init__(self):
        """Initialize the handler."""
        self.wrapper = XL2TimesWrapper()

    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run xl2times with the specified arguments.

        Args:
            arguments: Dictionary containing xl2times parameters

        Returns:
            Dictionary with execution results
        """
        logger.info("Processing xl2times_run request")
        start_time = time.time()

        # Extract and validate arguments
        input_files = arguments.get("input")
        if not input_files:
            raise ValueError("Input files or directory required")

        # Extract all arguments
        output_dir = arguments.get("output_dir")
        regions = arguments.get("regions", [])
        include_dummy_imports = arguments.get("include_dummy_imports", False)
        ground_truth_dir = arguments.get("ground_truth_dir")
        dd = arguments.get("dd", False)
        only_read = arguments.get("only_read", False)
        no_cache = arguments.get("no_cache", False)
        verbose = arguments.get("verbose", 0)

        try:
            # Execute xl2times
            wrapper_result = await self.wrapper.run(
                input_files=input_files,
                output_dir=output_dir,
                regions=regions,
                include_dummy_imports=include_dummy_imports,
                ground_truth_dir=ground_truth_dir,
                dd=dd,
                only_read=only_read,
                no_cache=no_cache,
                verbose=verbose
            )

            # Build response
            execution_time = time.time() - start_time
            
            # Extract output files if output directory exists
            output_files = []
            if output_dir and Path(output_dir).exists():
                output_files = [str(f) for f in Path(output_dir).rglob("*") if f.is_file()]

            result = {
                "success": wrapper_result.get("success", False),
                "output_files": output_files,
                "output_directory": output_dir or "default_output",
                "logs": wrapper_result.get("stdout", ""),
                "warnings": wrapper_result.get("warnings", []),
                "errors": wrapper_result.get("errors", []),
                "raw_tables": None,  # TODO: Parse raw_tables.txt if only_read=True
                "execution_time": execution_time,
                "message": wrapper_result.get("message", ""),
                "files_processed": wrapper_result.get("files_processed", []),
                "command": wrapper_result.get("command", "")
            }

            logger.info(f"xl2times_run completed in {execution_time:.2f}s")
            return result

        except XL2TimesError as e:
            logger.error(f"xl2times execution failed: {e}")
            execution_time = time.time() - start_time
            
            # Return error response
            return {
                "success": False,
                "output_files": [],
                "output_directory": output_dir or "default_output",
                "logs": "",
                "warnings": [],
                "errors": [str(e)],
                "raw_tables": None,
                "execution_time": execution_time,
                "message": f"xl2times execution failed: {str(e)}",
                "files_processed": [],
                "command": ""
            }

        except Exception as e:
            logger.error(f"Unexpected error in xl2times handler: {e}")
            raise

