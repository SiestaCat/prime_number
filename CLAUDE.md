# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for finding and verifying very large prime numbers (millions of digits). The project supports both CPU and GPU computation modes with real-time progress tracking.

## Architecture

- **Language**: Python 3.8+
- **Purpose**: Prime number search/verification for extremely large numbers (millions of digits)
- **Computation**: Supports both CPU and GPU processing
- **Deployment**: Docker containerization for testing (CPU mode only)
- **Package Structure**:
  - `prime_checker/`: Main package
    - `cpu_algorithms.py`: CPU-based algorithms (Miller-Rabin, Lucas-Lehmer, BPSW, Lucas)
    - `gpu_algorithms.py`: GPU-accelerated algorithms using CuPy
    - `utils.py`: Utility functions for prime operations
    - `cli.py`: Command-line interface using Click
    - `progress.py`: Advanced progress tracking with time estimates
  - `tests/`: Comprehensive test suite using pytest
  - `prime_check`: Standalone executable script (no venv activation needed)

## Implemented Algorithms

1. **Miller-Rabin**: Fast probabilistic test with configurable rounds
2. **Lucas-Lehmer**: Deterministic test for Mersenne primes (2^p - 1)
3. **Baillie-PSW (BPSW)**: Combines Miller-Rabin and Lucas tests, no known pseudoprimes
4. **Lucas Primality Test**: Based on Lucas sequences

## Common Commands

```bash
# Setup virtual environment (first time)
./create_venv.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install for development
pip install -e ".[dev]"

# Install with GPU support
pip install -e ".[gpu]"

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=prime_checker --cov-report=html

# Check a number for primality (standalone - no venv activation needed)
./prime_check check 97
./prime_check check "2^127-1" --verbose
./prime_check check 1000000007 --algorithm bpsw

# Generate prime numbers
./prime_check generate --bits 256 --count 5
./prime_check generate --mersenne --count 3

# Batch check from file
./prime_check batch numbers.txt --output results.txt

# Alternative: with venv activation
source venv/bin/activate && prime-check check 97

# Build Docker image
docker build -t prime-checker .

# Run with Docker
docker run --rm prime-checker check 97
docker run --rm -v $(pwd)/data:/app/data prime-checker batch /app/data/numbers.txt

# Run tests in Docker
docker-compose up prime-checker-test
```

## Development Workflow

1. **Environment Setup**: Always work within the virtual environment (`source venv/bin/activate`)
2. **Testing**: ALWAYS run tests after making changes:
   ```bash
   # Quick test run
   source venv/bin/activate && pytest
   
   # Full test with coverage
   source venv/bin/activate && pytest --cov=prime_checker --cov-report=html
   
   # Test specific changes
   source venv/bin/activate && pytest tests/test_cpu_algorithms.py -v
   ```
3. **Type Checking**: Code uses type hints extensively
4. **Large Numbers**: Use `gmpy2.mpz` for arbitrary precision arithmetic
5. **GPU Code**: GPU functionality is optional and gracefully falls back to CPU
6. **CLI Design**: All functionality is accessible through the `prime-check` command
7. **Progress Integration**: When adding new algorithms, integrate with progress system from `progress.py`

## Key Implementation Details

1. **Number Input**: Supports regular numbers, expressions (e.g., "10**100 + 3"), and Mersenne format ("2^p-1")
2. **Algorithm Selection**: "auto" mode intelligently selects the best algorithm
3. **Memory Efficiency**: Uses gmpy2 for efficient large number operations
4. **Progress Feedback**: Real-time progress with time estimates and 2-decimal precision percentages
5. **Error Handling**: Graceful handling of invalid inputs and GPU unavailability
6. **Standalone Execution**: `./prime_check` script works without manual venv activation

## Performance Considerations

1. **CPU Optimization**: Uses gmpy2's optimized modular arithmetic
2. **GPU Limitations**: GPU implementation falls back to CPU for very large numbers (> 64 bits)
3. **Batch Processing**: Efficient parallel testing with progress tracking
4. **Mersenne Numbers**: Special optimizations for 2^p - 1 format
5. **Progress System**: Minimal overhead progress tracking with accurate time estimation

## Progress System Features

- **Real-time Updates**: Shows elapsed time, remaining time, and completion percentage
- **Smart Thresholds**: Only shows progress for computations that warrant it
- **Batch Operations**: Tracks overall progress and individual results
- **Time Estimation**: Uses completion ratio to estimate remaining time
- **Percentage Precision**: Displays progress with 2 decimal places (e.g., 67.24%)

## Testing Guidelines

### When to Run Tests
- **ALWAYS** after modifying algorithm code
- **ALWAYS** before committing changes
- **ALWAYS** after adding new features
- After updating dependencies
- Before creating pull requests

### Test Coverage Requirements
- All new algorithms must have unit tests
- CLI commands must have integration tests
- Progress functionality must be tested
- Error handling must be tested

### Test Categories to Run
```bash
# After algorithm changes
pytest tests/test_cpu_algorithms.py tests/test_utils.py

# After CLI changes  
pytest tests/test_cli.py tests/test_standalone_script.py

# After progress system changes
pytest tests/test_progress.py

# Full test suite (required before commit)
pytest --cov=prime_checker
```