"""Tests for xl2times wrapper module."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest

from src.wrappers.xl2times_wrapper import XL2TimesWrapper, XL2TimesError


class TestXL2TimesWrapper:
    """Test cases for XL2TimesWrapper."""

    @pytest.fixture
    def wrapper(self):
        """Create wrapper instance."""
        return XL2TimesWrapper()

    def test_command_construction_basic(self, wrapper):
        """Test basic command construction."""
        cmd = wrapper._build_command(
            input_files="model.xlsx",
            output_dir="output"
        )
        assert cmd == ["uvx", "xl2times", "model.xlsx", "--output_dir", "output"]

    def test_command_construction_with_list_input(self, wrapper):
        """Test command construction with list of input files."""
        cmd = wrapper._build_command(
            input_files=["model1.xlsx", "model2.xlsx"],
            output_dir="output"
        )
        assert cmd == ["uvx", "xl2times", "model1.xlsx", "model2.xlsx", "--output_dir", "output"]

    def test_command_construction_with_regions(self, wrapper):
        """Test command construction with regions."""
        cmd = wrapper._build_command(
            input_files="model.xlsx",
            regions=["USA", "EUR"]
        )
        assert cmd == ["uvx", "xl2times", "model.xlsx", "--regions", "USA", "EUR"]

    def test_command_construction_with_all_options(self, wrapper):
        """Test command construction with all options."""
        cmd = wrapper._build_command(
            input_files="model.xlsx",
            output_dir="output",
            regions=["USA"],
            include_dummy_imports=True,
            ground_truth_dir="gt_dir",
            dd=True,
            only_read=True,
            no_cache=True,
            verbose=2
        )
        
        assert "uvx" in cmd
        assert "xl2times" in cmd
        assert "model.xlsx" in cmd
        assert "--output_dir" in cmd
        assert "output" in cmd
        assert "--regions" in cmd
        assert "USA" in cmd
        assert "--include_dummy_imports" in cmd
        assert "--ground_truth_dir" in cmd
        assert "gt_dir" in cmd
        assert "--dd" in cmd
        assert "--only_read" in cmd
        assert "--no_cache" in cmd
        assert "-v" in cmd
        assert cmd.count("-v") == 2

    @pytest.mark.asyncio
    async def test_run_success(self, wrapper):
        """Test successful xl2times execution."""
        with patch('asyncio.create_subprocess_exec') as mock_exec, \
             patch('builtins.open', mock_open()) as mock_file:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(
                b"Excel files successfully converted to CSV",
                None  # stderr combined into stdout
            ))
            mock_exec.return_value = mock_process

            result = await wrapper.run(
                input_files="model.xlsx",
                output_dir="output"
            )

            assert result["success"] is True
            assert result["return_code"] == 0
            assert result["log_file"]  # Should have log file path
            assert "output_files" in result
            assert "message" in result

    @pytest.mark.asyncio
    async def test_run_with_error(self, wrapper):
        """Test xl2times execution with error."""
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Mock process with error
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(
                b"",
                b"Error: Input file not found"
            ))
            mock_exec.return_value = mock_process

            with pytest.raises(XL2TimesError) as exc_info:
                await wrapper.run(
                    input_files="missing.xlsx",
                    output_dir="output"
                )
            
            assert "Input file not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_timeout(self, wrapper):
        """Test xl2times execution timeout."""
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Mock process that times out
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            mock_process.kill = MagicMock()  # Use regular mock for kill
            mock_process.wait = AsyncMock(return_value=None)
            mock_exec.return_value = mock_process

            with pytest.raises(XL2TimesError) as exc_info:
                await wrapper.run(
                    input_files="model.xlsx",
                    output_dir="output"
                )
            
            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_check_xl2times_available(self, wrapper):
        """Test checking if xl2times is available."""
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Mock successful help command
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(
                b"xl2times version 0.1.0",
                b""
            ))
            mock_exec.return_value = mock_process

            available = await wrapper.check_xl2times_available()
            assert available is True

    @pytest.mark.asyncio
    async def test_check_xl2times_not_available(self, wrapper):
        """Test checking xl2times when not available."""
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Mock failed command
            mock_exec.side_effect = FileNotFoundError()

            available = await wrapper.check_xl2times_available()
            assert available is False

    def test_parse_output_basic(self, wrapper):
        """Test parsing basic xl2times output."""
        stdout = """
        Reading model files...
        Processing Sets-DemoModels.xlsx
        Processing SysSettings.xlsx
        Excel files successfully converted to CSV and written to output
        """
        
        parsed = wrapper._parse_output(stdout, "")
        
        assert parsed["success"] is True
        assert "Excel files successfully converted" in parsed["message"]
        assert len(parsed["files_processed"]) == 2
        assert "Sets-DemoModels.xlsx" in parsed["files_processed"]

    def test_parse_output_with_warnings(self, wrapper):
        """Test parsing output with warnings."""
        stdout = """
        Processing file...
        WARNING: Dropping table with unrecognized tag
        WARNING: Missing data in column X
        FutureWarning: Setting an item of incompatible dtype is deprecated
        Excel files successfully converted to CSV
        """
        
        parsed = wrapper._parse_output(stdout, "")
        
        assert parsed["success"] is True
        assert len(parsed["warnings"]) == 3
        assert any("unrecognized tag" in w for w in parsed["warnings"])
        assert any("incompatible dtype" in w for w in parsed["warnings"])

    def test_parse_output_with_errors(self, wrapper):
        """Test parsing output with errors."""
        stderr = """
        Error: Cannot read file model.xlsx
        Error: Invalid format in sheet ABC
        """
        
        parsed = wrapper._parse_output("", stderr)
        
        assert parsed["success"] is False
        assert len(parsed["errors"]) == 2
        assert any("Cannot read file" in e for e in parsed["errors"])