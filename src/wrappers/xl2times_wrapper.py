"""Wrapper for xl2times command execution."""

import asyncio
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from ..config import config


class XL2TimesError(Exception):
    """Exception raised for xl2times execution errors."""
    pass


class XL2TimesWrapper:
    """Wrapper for executing xl2times commands."""

    def __init__(self):
        """Initialize the wrapper."""
        self.command = config.XL2TIMES_COMMAND.split()
        self.timeout = config.XL2TIMES_TIMEOUT

    async def run(
        self,
        input_files: Union[str, List[str]],
        output_dir: Optional[str] = None,
        regions: Optional[List[str]] = None,
        include_dummy_imports: bool = False,
        ground_truth_dir: Optional[str] = None,
        dd: bool = False,
        only_read: bool = False,
        no_cache: bool = False,
        verbose: int = 0
    ) -> Dict[str, Any]:
        """
        Execute xl2times with the specified parameters.

        Args:
            input_files: Input directory or list of xlsx/xlsm files
            output_dir: Output directory for generated files
            regions: List of regions to include
            include_dummy_imports: Include dummy import processes
            ground_truth_dir: Ground truth directory for comparison
            dd: Output DD files
            only_read: Only read files and output raw_tables.txt
            no_cache: Ignore cache and re-extract from XLSX
            verbose: Verbosity level (0-4)

        Returns:
            Dictionary with execution results

        Raises:
            XL2TimesError: If execution fails
        """
        # Build command
        cmd = self._build_command(
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

        logger.info(f"Executing xl2times command: {' '.join(cmd)}")

        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise XL2TimesError(f"xl2times execution timed out after {self.timeout} seconds")

            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            # Check return code
            if process.returncode != 0:
                error_msg = stderr_str or stdout_str or f"xl2times failed with return code {process.returncode}"
                raise XL2TimesError(error_msg)

            # Parse output
            result = self._parse_output(stdout_str, stderr_str)
            result.update({
                "stdout": stdout_str,
                "stderr": stderr_str,
                "return_code": process.returncode,
                "command": ' '.join(cmd)
            })

            logger.info("xl2times execution completed successfully")
            return result

        except FileNotFoundError:
            raise XL2TimesError(f"xl2times command not found: {' '.join(self.command)}")
        except Exception as e:
            if isinstance(e, XL2TimesError):
                raise
            raise XL2TimesError(f"xl2times execution failed: {str(e)}")

    def _build_command(
        self,
        input_files: Union[str, List[str]],
        output_dir: Optional[str] = None,
        regions: Optional[List[str]] = None,
        include_dummy_imports: bool = False,
        ground_truth_dir: Optional[str] = None,
        dd: bool = False,
        only_read: bool = False,
        no_cache: bool = False,
        verbose: int = 0
    ) -> List[str]:
        """Build xl2times command with arguments."""
        cmd = self.command.copy()

        # Add input files
        if isinstance(input_files, str):
            cmd.append(input_files)
        else:
            cmd.extend(input_files)

        # Add optional arguments
        if output_dir:
            cmd.extend(["--output_dir", output_dir])

        if regions:
            cmd.append("--regions")
            cmd.extend(regions)

        if include_dummy_imports:
            cmd.append("--include_dummy_imports")

        if ground_truth_dir:
            cmd.extend(["--ground_truth_dir", ground_truth_dir])

        if dd:
            cmd.append("--dd")

        if only_read:
            cmd.append("--only_read")

        if no_cache:
            cmd.append("--no_cache")

        if verbose > 0:
            # xl2times uses -v flags, multiple for higher verbosity
            for _ in range(min(verbose, 4)):  # Cap at 4 levels
                cmd.append("-v")

        return cmd

    def _parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse xl2times output to extract relevant information."""
        result = {
            "success": False,
            "message": "",
            "files_processed": [],
            "warnings": [],
            "errors": [],
            "output_files": []
        }

        # Check for success message or completion indicators
        success_indicators = [
            "successfully converted",
            "Excel files successfully converted to CSV",
            "written to output"
        ]
        
        for indicator in success_indicators:
            if indicator in stdout.lower():
                result["success"] = True
                result["message"] = "Excel files successfully converted"
                break

        # Extract processed files
        for line in stdout.split('\n'):
            # Look for file processing messages
            if re.match(r'.*Processing\s+(\S+\.xlsx?)', line):
                match = re.search(r'Processing\s+(\S+\.xlsx?)', line)
                if match:
                    result["files_processed"].append(match.group(1))

        # Extract warnings from stdout
        for line in stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for various warning patterns
            warning_match = None
            if re.search(r'WARNING\s*:', line, re.IGNORECASE):
                warning_match = re.search(r'WARNING\s*:\s*(.+)', line, re.IGNORECASE)
            elif re.search(r'FutureWarning\s*:', line, re.IGNORECASE):
                warning_match = re.search(r'FutureWarning\s*:\s*(.+)', line, re.IGNORECASE)
            elif re.search(r'UserWarning\s*:', line, re.IGNORECASE):
                warning_match = re.search(r'UserWarning\s*:\s*(.+)', line, re.IGNORECASE)
            elif re.search(r'DeprecationWarning\s*:', line, re.IGNORECASE):
                warning_match = re.search(r'DeprecationWarning\s*:\s*(.+)', line, re.IGNORECASE)
            
            if warning_match:
                result["warnings"].append(warning_match.group(1).strip())

        # Extract actual errors from stderr (exclude warnings)
        if stderr:
            for line in stderr.split('\n'):
                line = line.strip()
                if line and 'error' in line.lower():
                    # Skip if it's actually a warning disguised as error in stderr
                    if any(warn_type in line.lower() for warn_type in ['warning', 'futurewarning', 'userwarning', 'deprecationwarning']):
                        # Treat as warning instead
                        result["warnings"].append(line)
                    else:
                        result["errors"].append(line)

        # Determine final success status
        # If we haven't found success indicators but have no real errors and have output, assume success
        if not result["success"] and not result["errors"]:
            # Look for signs of completion in stdout
            if any(indicator in stdout.lower() for indicator in [
                "loading", "extracted", "transform", "took", "seconds"
            ]):
                result["success"] = True
                result["message"] = "Processing completed"

        # Only mark as failed if we have actual errors (not warnings)
        if result["errors"]:
            result["success"] = False
            result["message"] = "Errors occurred during conversion"
        elif result["success"] and result["warnings"]:
            result["message"] = f"Conversion completed with {len(result['warnings'])} warnings"

        return result

    async def check_xl2times_available(self) -> bool:
        """Check if xl2times is available and executable."""
        try:
            cmd = self.command + ["--help"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=10)
            return process.returncode == 0
            
        except (FileNotFoundError, asyncio.TimeoutError, Exception):
            return False