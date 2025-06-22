"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner
from prime_checker.cli import main
import tempfile
import os


class TestCLI:
    """Test command-line interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_version(self):
        """Test version command."""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_check_prime(self):
        """Test checking prime numbers."""
        # Test with a prime
        result = self.runner.invoke(main, ['check', '97'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
        
        # Test with a composite
        result = self.runner.invoke(main, ['check', '98'])
        assert result.exit_code == 1
        assert 'COMPOSITE' in result.output
    
    def test_check_mersenne(self):
        """Test checking Mersenne numbers."""
        # M7 = 127 is prime
        result = self.runner.invoke(main, ['check', '2^7-1'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
        
        # M11 = 2047 is composite
        result = self.runner.invoke(main, ['check', '2^11-1'])
        assert result.exit_code == 1
        assert 'COMPOSITE' in result.output
    
    def test_check_expression(self):
        """Test checking expressions."""
        # 2^5 = 32 (composite)
        result = self.runner.invoke(main, ['check', '2^5'])
        assert result.exit_code == 1
        assert 'COMPOSITE' in result.output
        
        # 10**6 + 3 = 1000003 (prime)
        result = self.runner.invoke(main, ['check', '10**6 + 3'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
    
    def test_check_verbose(self):
        """Test verbose output."""
        result = self.runner.invoke(main, ['check', '97', '--verbose'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
        assert 'Computation time' in result.output
        assert 'Number of digits' in result.output
        assert 'Number of bits' in result.output
    
    def test_check_algorithms(self):
        """Test different algorithms."""
        # Miller-Rabin
        result = self.runner.invoke(main, ['check', '97', '-a', 'miller-rabin'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
        
        # BPSW
        result = self.runner.invoke(main, ['check', '97', '-a', 'bpsw'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output
    
    def test_generate_primes(self):
        """Test prime generation."""
        result = self.runner.invoke(main, ['generate', '-b', '16', '-c', '3'])
        assert result.exit_code == 0
        assert 'Generating 3 16-bit' in result.output
        assert result.output.count('Generated:') == 3
    
    def test_generate_mersenne(self):
        """Test Mersenne prime candidate generation."""
        result = self.runner.invoke(main, ['generate', '-m', '-c', '2', '-b', '10'])
        assert result.exit_code == 0
        assert 'Mersenne prime candidates' in result.output
        assert 'M' in result.output
    
    def test_generate_with_output(self):
        """Test saving generated primes to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = self.runner.invoke(main, ['generate', '-b', '16', '-c', '5', '-o', output_file])
            assert result.exit_code == 0
            assert f'Saved 5 primes to {output_file}' in result.output
            
            # Check file contents
            with open(output_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 5
                for line in lines:
                    assert line.strip().isdigit()
        finally:
            os.unlink(output_file)
    
    def test_batch_check(self):
        """Test batch checking from file."""
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("97\n")
            f.write("98\n")
            f.write("2^7-1\n")
            f.write("2^11-1\n")
            input_file = f.name
        
        try:
            result = self.runner.invoke(main, ['batch', input_file])
            assert result.exit_code == 0
            assert 'Testing 4 numbers' in result.output
            assert 'Prime: 2' in result.output
            assert 'Composite: 2' in result.output
        finally:
            os.unlink(input_file)
    
    def test_batch_with_output(self):
        """Test batch checking with output file."""
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("97\n")
            f.write("98\n")
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            output_file = f.name
        
        try:
            result = self.runner.invoke(main, ['batch', input_file, '-o', output_file])
            assert result.exit_code == 0
            assert f'Results saved to {output_file}' in result.output
            
            # Check output file
            with open(output_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 2
                assert '97\tPRIME' in lines[0]
                assert '98\tCOMPOSITE' in lines[1]
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_info_command(self):
        """Test info command."""
        result = self.runner.invoke(main, ['info'])
        assert result.exit_code == 0
        assert 'Prime Number Checker v1.0.0' in result.output
        assert 'GPU Support:' in result.output
        assert 'Supported algorithms:' in result.output
        assert 'Miller-Rabin' in result.output
        assert 'Lucas-Lehmer' in result.output
        assert 'Baillie-PSW' in result.output
    
    def test_invalid_number(self):
        """Test with invalid input."""
        result = self.runner.invoke(main, ['check', 'invalid'])
        assert result.exit_code == 2
        assert 'Error:' in result.output
    
    def test_check_rounds_option(self):
        """Test custom rounds for Miller-Rabin."""
        result = self.runner.invoke(main, ['check', '97', '-a', 'miller-rabin', '-r', '5'])
        assert result.exit_code == 0
        assert 'PRIME' in result.output