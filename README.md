# Prime Number Checker

A high-performance prime number checker for very large numbers (millions of digits) with CPU and GPU support, featuring real-time progress tracking and standalone execution.

## Features

- **Multiple Algorithms**: Miller-Rabin, Lucas-Lehmer, Baillie-PSW, and Lucas primality tests
- **CPU/GPU Support**: Leverage GPU acceleration for parallel computations
- **Large Number Support**: Handle numbers with millions of digits using gmpy2
- **Mersenne Prime Testing**: Specialized support for Mersenne numbers (2^p - 1)
- **Batch Processing**: Test multiple numbers efficiently with progress tracking
- **Real-time Progress**: Time estimates and percentage tracking with 2-decimal precision
- **Standalone Execution**: Run without manual virtual environment activation
- **Docker Support**: Containerized deployment for easy testing

## Installation

### Quick Setup with Virtual Environment
```bash
# Clone the repository
git clone <repository-url>
cd prime_number

# Create and setup virtual environment
./create_venv.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
```

### CPU-only Installation
```bash
pip install -e .
```

### GPU-enabled Installation
```bash
pip install -e ".[gpu]"
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## Usage

### Check a Single Number
```bash
# Check if a number is prime (standalone - no venv activation needed)
./prime_check check 97

# Check a Mersenne number with progress tracking
./prime_check check "2^127-1" --verbose

# Check with verbose output
./prime_check check 1000000007 --verbose

# Use specific algorithm
./prime_check check 97 --algorithm miller-rabin --rounds 20

# Use GPU acceleration
./prime_check check 97 --use-gpu

# Alternative: with manual venv activation
source venv/bin/activate && prime-check check 97
```

### Generate Prime Numbers
```bash
# Generate 5 random 256-bit primes with progress
./prime_check generate --bits 256 --count 5

# Generate Mersenne prime candidates
./prime_check generate --mersenne --count 3

# Save to file
./prime_check generate --bits 512 --count 10 --output primes.txt
```

### Batch Processing
```bash
# Check multiple numbers from a file with progress tracking
./prime_check batch numbers.txt

# Save results with progress
./prime_check batch numbers.txt --output results.txt

# Use GPU for batch processing
./prime_check batch numbers.txt --use-gpu
```

### System Information
```bash
# Display system and GPU information
./prime_check info
```

## Docker Usage

### Build the Image
```bash
docker build -t prime-checker .
```

### Run with Docker
```bash
# Check a number
docker run --rm prime-checker check 97

# Generate primes
docker run --rm prime-checker generate --bits 256 --count 5

# Mount volume for file I/O
docker run --rm -v $(pwd)/data:/app/data prime-checker batch /app/data/numbers.txt
```

### Run Tests with Docker
```bash
# Using docker-compose
docker-compose up prime-checker-test

# Or directly with Docker
docker build -f Dockerfile.test -t prime-checker-test .
docker run --rm prime-checker-test
```

## Algorithms

### Miller-Rabin
- Fast probabilistic primality test
- Configurable number of rounds
- Deterministic for numbers < 3,317,044,064,679,887,385,961,981

### Lucas-Lehmer
- Specialized for Mersenne primes (2^p - 1)
- Deterministic test
- Progress bar for large exponents

### Baillie-PSW (BPSW)
- Combines Miller-Rabin and Lucas tests
- No known pseudoprimes
- Recommended for general use

### Lucas Primality Test
- Based on Lucas sequences
- Strong primality test
- Part of BPSW composite test

## Performance

- **CPU**: Optimized using gmpy2 for arbitrary precision arithmetic
- **GPU**: CUDA acceleration for parallel testing (requires NVIDIA GPU)
- **Memory**: Efficient handling of numbers with millions of digits
- **Parallelization**: Batch processing with real-time progress tracking
- **Progress System**: Minimal overhead with accurate time estimation

## Progress Features

The application includes a sophisticated progress tracking system:

- **Real-time Updates**: Shows elapsed time, estimated remaining time, and completion percentage
- **Precision**: Percentages displayed with 2 decimal places (e.g., 67.24%)
- **Smart Display**: Only shows progress bars for operations that warrant them
- **Batch Tracking**: Monitors overall progress and individual test results
- **Time Estimation**: Uses completion ratios to provide accurate time estimates

Example progress output:
```
Lucas-Lehmer M127 (67.24%):  67%|██████▋   | 84/125 [00:00<00:00, 15086.78iter/s] 67.24%
```

## Requirements

- Python 3.8+
- gmpy2 (for arbitrary precision arithmetic)
- numpy
- click (CLI framework)
- tqdm (progress bars)
- cupy (for GPU support, optional)

## License

MIT License