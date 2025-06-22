# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for finding and verifying very large prime numbers (millions of digits). The project supports both CPU and GPU computation modes.

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
  - `tests/`: Comprehensive test suite using pytest

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

# Check a number for primality
prime-check 97
prime-check "2^127-1" --verbose
prime-check 1000000007 --algorithm bpsw

# Generate prime numbers
prime-check generate --bits 256 --count 5
prime-check generate --mersenne --count 3

# Batch check from file
prime-check batch numbers.txt --output results.txt

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
2. **Testing**: Always run `pytest` before committing changes
3. **Type Checking**: Code uses type hints extensively
4. **Large Numbers**: Use `gmpy2.mpz` for arbitrary precision arithmetic
5. **GPU Code**: GPU functionality is optional and gracefully falls back to CPU
6. **CLI Design**: All functionality is accessible through the `prime-check` command

## Key Implementation Details

1. **Number Input**: Supports regular numbers, expressions (e.g., "10**100 + 3"), and Mersenne format ("2^p-1")
2. **Algorithm Selection**: "auto" mode intelligently selects the best algorithm
3. **Memory Efficiency**: Uses gmpy2 for efficient large number operations
4. **Progress Feedback**: Shows progress bars for long computations
5. **Error Handling**: Graceful handling of invalid inputs and GPU unavailability

## Performance Considerations

1. **CPU Optimization**: Uses gmpy2's optimized modular arithmetic
2. **GPU Limitations**: GPU implementation falls back to CPU for very large numbers (> 64 bits)
3. **Batch Processing**: Efficient parallel testing of multiple numbers
4. **Mersenne Numbers**: Special optimizations for 2^p - 1 format