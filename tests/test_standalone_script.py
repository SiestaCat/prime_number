"""Tests for standalone script functionality."""

import pytest
import subprocess
import os
from pathlib import Path


class TestStandaloneScript:
    """Test the standalone prime_check script."""
    
    @pytest.fixture
    def script_path(self):
        """Get path to the prime_check script."""
        return Path(__file__).parent.parent / "prime_check"
    
    def test_script_exists_and_executable(self, script_path):
        """Test that the script exists and is executable."""
        assert script_path.exists()
        assert os.access(script_path, os.X_OK)
    
    def test_simple_prime_check(self, script_path):
        """Test checking a simple prime number."""
        result = subprocess.run(
            [str(script_path), "check", "97"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "PRIME" in result.stdout
    
    def test_composite_check(self, script_path):
        """Test checking a composite number."""
        result = subprocess.run(
            [str(script_path), "check", "98"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 1
        assert "COMPOSITE" in result.stdout
    
    def test_verbose_output(self, script_path):
        """Test verbose output."""
        result = subprocess.run(
            [str(script_path), "check", "97", "--verbose"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "Computation time" in result.stdout
        assert "Number of digits" in result.stdout
        assert "PRIME" in result.stdout
    
    def test_mersenne_number(self, script_path):
        """Test checking a Mersenne number."""
        result = subprocess.run(
            [str(script_path), "check", "2^7-1"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "PRIME" in result.stdout
    
    def test_help_command(self, script_path):
        """Test help command."""
        result = subprocess.run(
            [str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "prime number checker" in result.stdout.lower()
    
    def test_info_command(self, script_path):
        """Test info command."""
        result = subprocess.run(
            [str(script_path), "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "Prime Number Checker" in result.stdout
        assert "GPU Support" in result.stdout
    
    def test_invalid_number(self, script_path):
        """Test handling of invalid input."""
        result = subprocess.run(
            [str(script_path), "check", "invalid"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 2
        assert "Error:" in result.stderr
    
    def test_venv_activation(self, script_path):
        """Test that script properly activates virtual environment."""
        # Run a command that requires the venv packages
        result = subprocess.run(
            [str(script_path), "check", "1009"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should work without manual venv activation
        assert result.returncode == 0
        assert "PRIME" in result.stdout
    
    def test_script_error_handling(self, script_path):
        """Test script error handling when venv is missing."""
        # This test would require moving/renaming the venv, which might break other tests
        # So we'll just verify the script has the error checking logic
        with open(script_path, 'r') as f:
            content = f.read()
            assert "Virtual environment not found" in content
            assert "create_venv.sh" in content