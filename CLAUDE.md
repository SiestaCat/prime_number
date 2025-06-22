# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for finding and verifying very large prime numbers (millions of digits). The project supports both CPU and GPU computation modes.

## Architecture

- **Language**: Python
- **Purpose**: Prime number search/verification for extremely large numbers (millions of digits)
- **Computation**: Supports both CPU and GPU processing
- **Deployment**: Docker containerization for testing (CPU mode only)

## Development Guidelines

### Prime Number Algorithms
- Focus on algorithms suitable for very large numbers (Miller-Rabin, Lucas-Lehmer for Mersenne primes, etc.)
- Implement efficient modular arithmetic for large integers
- Consider using libraries like `gmpy2` for arbitrary precision arithmetic

### CPU/GPU Implementation
- CPU implementation should use Python's native capabilities or specialized libraries
- GPU implementation may use CUDA (via PyCUDA or CuPy) or OpenCL
- Ensure clean separation between CPU and GPU code paths

### Docker Setup
- Dockerfile should include all CPU dependencies
- GPU functionality is excluded from Docker testing environment
- Container should be optimized for computational workloads

## Common Commands

```bash
# Run CPU tests
python -m pytest tests/

# Run prime verification (example)
python prime_check.py <number>

# Build Docker image
docker build -t prime-number-checker .

# Run Docker container
docker run prime-number-checker
```

## Key Considerations

1. **Memory Management**: Working with millions of digits requires careful memory handling
2. **Algorithm Selection**: Different algorithms are optimal for different number ranges
3. **Parallelization**: Consider using multiprocessing for CPU or batch processing for GPU
4. **Testing**: Include tests for both small (verifiable) and large prime numbers