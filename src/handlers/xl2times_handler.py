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

            # Build response optimized for LLM consumption
            execution_time = time.time() - start_time
            wrapper_result["execution_time"] = execution_time

            # Extract raw_tables content if only_read was used
            raw_tables_content = None
            if only_read and output_dir:
                raw_tables_path = Path(output_dir) / "raw_tables.txt"
                if raw_tables_path.exists():
                    try:
                        raw_tables_content = raw_tables_path.read_text(encoding='utf-8')
                    except Exception as e:
                        logger.warning(f"Could not read raw_tables.txt: {e}")

            # Return wrapper result directly (already optimized for LLM)
            result = wrapper_result.copy()
            result["raw_tables"] = raw_tables_content

            logger.info(f"xl2times_run completed in {execution_time:.2f}s")
            return result

        except XL2TimesError as e:
            logger.error(f"xl2times execution failed: {e}")
            execution_time = time.time() - start_time
            
            # Return error response in LLM-optimized format
            return {
                "success": False,
                "return_code": -1,
                "log_file": "",
                "output_files": [],
                "output_directory": output_dir or "",
                "warnings": [],
                "errors": [str(e)],
                "files_processed": [],
                "execution_time": execution_time,
                "command": "",
                "message": f"xl2times execution failed: {str(e)}",
                "raw_tables": None
            }

        except Exception as e:
            logger.error(f"Unexpected error in xl2times handler: {e}")
            raise

