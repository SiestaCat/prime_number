# Running Prime Number Checker in Google Colab

This guide explains how to use the Prime Number Checker library in Google Colab for testing very large prime numbers.

## Quick Start

### 1. Install Dependencies

```python
# Install required packages (CPU-only for better Colab compatibility)
!pip install gmpy2 numpy click tqdm

# Clone the repository
!git clone https://github.com/SiestaCat/prime_number.git
%cd prime_number

# Install the package
!pip install -e .

# Verify installation works
from prime_checker import is_prime_cpu
print("✅ Installation successful!")
print(f"Test: 97 is prime = {is_prime_cpu(97)}")
```

### 1a. GPU Installation (Advanced - May Have Issues)

```python
# Install packages with GPU support (warning: often fails in Colab)
!pip install gmpy2 numpy click tqdm cupy-cuda12x

# Clone the repository
!git clone https://github.com/SiestaCat/prime_number.git
%cd prime_number

# Install with GPU support
!pip install -e ".[gpu]"

# Test if GPU actually works (often fails)
try:
    from prime_checker.gpu_algorithms import GPU_AVAILABLE
    print(f"GPU libraries installed: {GPU_AVAILABLE}")
    
    if GPU_AVAILABLE:
        import cupy as cp
        test = cp.array([1, 2, 3])
        print("✅ GPU test successful!")
    else:
        print("⚠️ GPU libraries not available")
        
except Exception as e:
    print(f"❌ GPU Error: {e}")
    print("💡 Recommendation: Use CPU-only installation below")
```

### 1b. CPU-Only Installation (Recommended for Colab)

```python
# If you encounter any GPU/CUDA issues, use this instead:

# Install without GPU dependencies
!pip install gmpy2 numpy click tqdm
!git clone https://github.com/SiestaCat/prime_number.git
%cd prime_number

# Force CPU-only mode
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Install package
!pip install -e .

# Test CPU-only functionality
from prime_checker.cpu_algorithms import is_prime_cpu
print("✅ CPU-only installation successful!")
print(f"Test: 97 is prime = {is_prime_cpu(97)}")
```

### 2. Basic Usage

```python
# Import the library
from prime_checker import is_prime_cpu, generate_random_probable_prime
from prime_checker.utils import generate_mersenne_candidate
import gmpy2

# Test small primes
print("Testing small numbers:")
print(f"97 is prime: {is_prime_cpu(97)}")
print(f"98 is prime: {is_prime_cpu(98)}")
```

### 3. Test Large Numbers

```python
# Test a large prime
large_prime = "1000000007"
print(f"{large_prime} is prime: {is_prime_cpu(large_prime)}")

# Test expressions
result = is_prime_cpu("10**100 + 267")
print(f"10^100 + 267 is prime: {result}")
```

### 4. Mersenne Prime Testing

```python
# Test Mersenne numbers
print("\nTesting Mersenne numbers:")

# M7 = 2^7 - 1 = 127 (known prime)
M7 = generate_mersenne_candidate(7)
print(f"M7 = 2^7 - 1 = {M7}")
print(f"M7 is prime: {is_prime_cpu(M7, algorithm='lucas-lehmer', p=7)}")

# M11 = 2^11 - 1 = 2047 (composite)
M11 = generate_mersenne_candidate(11)
print(f"M11 = 2^11 - 1 = {M11}")
print(f"M11 is prime: {is_prime_cpu(M11, algorithm='lucas-lehmer', p=11)}")
```

### 5. Generate Random Primes

```python
# Generate random probable primes
print("\nGenerating random primes:")

for bits in [32, 64, 128]:
    prime = generate_random_probable_prime(bits)
    print(f"{bits}-bit prime: {prime}")
    print(f"Verification: {is_prime_cpu(prime)}")
    print()
```

## Advanced Examples

### Large Mersenne Prime Testing with Progress

```python
# Test larger Mersenne numbers (with progress tracking)
print("Testing larger Mersenne numbers:")

# M31 = 2^31 - 1 (known prime)
print("Testing M31 = 2^31 - 1...")
result = is_prime_cpu(2**31 - 1, algorithm='lucas-lehmer', p=31, show_progress=True)
print(f"M31 is prime: {result}")
```

### Batch Testing

```python
# Test multiple numbers
test_numbers = [
    97,
    101,
    1009,
    10007,
    "10**6 + 3",
    2**31 - 1,  # M31
    2**13 - 1,  # M13
]

print("Batch testing:")
for num in test_numbers:
    try:
        result = is_prime_cpu(num)
        print(f"{str(num)[:50]}: {'PRIME' if result else 'COMPOSITE'}")
    except Exception as e:
        print(f"{str(num)[:50]}: ERROR - {e}")
```

### Testing Prime Numbers from Text File

```python
# Create a sample text file with numbers to test
sample_numbers = """97
101
1009
10007
1000000007
2^31-1
2^13-1
10**100 + 267
12345678901234567890123456789012345678901234567890123456789061"""

# Save to file
with open('numbers_to_test.txt', 'w') as f:
    f.write(sample_numbers)

print("Created numbers_to_test.txt with sample numbers")
```

```python
# Method 1: Test numbers from file with progress tracking
def test_numbers_from_file(filename, show_progress=True):
    """Test prime numbers from a text file."""
    results = []
    
    # Read numbers from file
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Testing {len(lines)} numbers from {filename}:")
    print("-" * 60)
    
    for i, line in enumerate(lines):
        print(f"\n[{i+1}/{len(lines)}] Testing: {line[:50]}{'...' if len(line) > 50 else ''}")
        
        try:
            # Parse different number formats
            if line.startswith('2^') and '-1' in line:
                # Mersenne number format: 2^p-1
                p = int(line[2:line.index('-1')])
                n = 2**p - 1
                print(f"  Mersenne M{p} = 2^{p} - 1")
                print(f"  Number has {len(str(n))} decimal digits")
                
                # Use Lucas-Lehmer for Mersenne numbers
                result = is_prime_cpu(n, algorithm='lucas-lehmer', p=p, show_progress=show_progress)
            elif '**' in line or '+' in line or '-' in line:
                # Expression format
                n = eval(line)
                print(f"  Evaluated to: {str(n)[:100]}{'...' if len(str(n)) > 100 else ''}")
                result = is_prime_cpu(n, show_progress=show_progress)
            else:
                # Regular number
                n = int(line)
                result = is_prime_cpu(n, show_progress=show_progress)
            
            status = "PRIME" if result else "COMPOSITE"
            color = "✅" if result else "❌"
            print(f"  Result: {color} {status}")
            
            results.append((line, result, None))
            
        except Exception as e:
            print(f"  Result: ⚠️ ERROR - {str(e)}")
            results.append((line, None, str(e)))
    
    return results

# Test the numbers
results = test_numbers_from_file('numbers_to_test.txt', show_progress=True)
```

```python
# Method 2: Upload your own file from local computer
from google.colab import files

print("Upload a text file with numbers (one per line):")
uploaded = files.upload()

# Get the uploaded filename
filename = list(uploaded.keys())[0]
print(f"Uploaded file: {filename}")

# Test the uploaded numbers
results = test_numbers_from_file(filename, show_progress=True)
```

```python
# Generate summary report
def generate_report(results, save_to_file=True):
    """Generate a summary report of the test results."""
    
    print("\n" + "="*80)
    print("PRIME NUMBER TEST SUMMARY")
    print("="*80)
    
    prime_count = sum(1 for _, result, error in results if result is True)
    composite_count = sum(1 for _, result, error in results if result is False)
    error_count = sum(1 for _, result, error in results if error is not None)
    
    print(f"Total numbers tested: {len(results)}")
    print(f"Prime numbers found: {prime_count}")
    print(f"Composite numbers: {composite_count}")
    print(f"Errors encountered: {error_count}")
    print()
    
    # Show primes found
    if prime_count > 0:
        print("PRIME NUMBERS FOUND:")
        print("-" * 40)
        for number, result, error in results:
            if result is True:
                display_num = number[:60] + "..." if len(number) > 60 else number
                print(f"✅ {display_num}")
        print()
    
    # Show errors if any
    if error_count > 0:
        print("ERRORS ENCOUNTERED:")
        print("-" * 40)
        for number, result, error in results:
            if error is not None:
                display_num = number[:40] + "..." if len(number) > 40 else number
                print(f"⚠️ {display_num}: {error}")
        print()
    
    # Save detailed report
    if save_to_file:
        report_filename = 'prime_test_report.txt'
        with open(report_filename, 'w') as f:
            f.write("PRIME NUMBER TEST REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total numbers tested: {len(results)}\n")
            f.write(f"Prime numbers found: {prime_count}\n")
            f.write(f"Composite numbers: {composite_count}\n")
            f.write(f"Errors encountered: {error_count}\n\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for number, result, error in results:
                if error:
                    status = f"ERROR: {error}"
                elif result is True:
                    status = "PRIME"
                else:
                    status = "COMPOSITE"
                f.write(f"{number}\t{status}\n")
        
        print(f"Detailed report saved to: {report_filename}")
        
        # Option to download the report
        from google.colab import files
        files.download(report_filename)

# Generate and save the report
generate_report(results)
```

```python
# Advanced: Test very large numbers from file with time tracking
import time

def test_large_numbers_with_timing(filename):
    """Test large numbers with detailed timing information."""
    
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print("LARGE NUMBER TESTING WITH TIMING")
    print("=" * 50)
    
    total_time = 0
    
    for i, line in enumerate(lines):
        print(f"\n[{i+1}/{len(lines)}] {line[:40]}{'...' if len(line) > 40 else ''}")
        
        try:
            start_time = time.time()
            
            # Parse and test
            if line.startswith('2^') and '-1' in line:
                p = int(line[2:line.index('-1')])
                n = 2**p - 1
                digits = len(str(n))
                print(f"  Mersenne M{p} ({digits:,} digits)")
                result = is_prime_cpu(n, algorithm='lucas-lehmer', p=p, show_progress=False)
            else:
                if '**' in line or '+' in line:
                    n = eval(line)
                else:
                    n = int(line)
                digits = len(str(n))
                print(f"  Regular number ({digits:,} digits)")
                result = is_prime_cpu(n, show_progress=False)
            
            elapsed = time.time() - start_time
            total_time += elapsed
            
            status = "PRIME" if result else "COMPOSITE"
            print(f"  Result: {status}")
            print(f"  Time: {elapsed:.3f} seconds")
            
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"  Error: {e}")
            print(f"  Time: {elapsed:.3f} seconds")
    
    print(f"\nTotal testing time: {total_time:.3f} seconds")
    print(f"Average time per number: {total_time/len(lines):.3f} seconds")

# Run timing test
test_large_numbers_with_timing('prime_number.txt')
```

### Algorithm Comparison

```python
# Compare different algorithms
import time

def time_algorithm(n, algorithm, **kwargs):
    start = time.time()
    result = is_prime_cpu(n, algorithm=algorithm, **kwargs)
    elapsed = time.time() - start
    return result, elapsed

# Test number
test_num = 1000000007

print("Algorithm comparison:")
algorithms = ['miller-rabin', 'bpsw']

for algo in algorithms:
    try:
        result, elapsed = time_algorithm(test_num, algo)
        print(f"{algo:15}: {result} ({elapsed:.4f}s)")
    except Exception as e:
        print(f"{algo:15}: ERROR - {e}")
```

### Working with Very Large Numbers

```python
# Test very large numbers (millions of digits)
print("Testing very large numbers:")

# Generate a large number
large_base = 10**1000
candidates = [large_base + i for i in [3, 7, 9, 21, 33]]

print(f"Testing numbers around 10^1000 ({len(str(large_base))} digits):")
for i, num in enumerate(candidates):
    print(f"Candidate {i+1}: {str(num)[:50]}...{str(num)[-10:]}")
    try:
        result = is_prime_cpu(num, algorithm='miller-rabin', rounds=10)
        print(f"Result: {'PRIME' if result else 'COMPOSITE'}")
    except Exception as e:
        print(f"Error: {e}")
    print()
```

## Performance Tips for Colab

### 1. Check GPU Availability (Important Note)

```python
# Check if GPU libraries are available and working
def check_gpu_support():
    """Check if GPU acceleration is available and working."""
    try:
        from prime_checker.gpu_algorithms import GPU_AVAILABLE
        print(f"CuPy installed: {GPU_AVAILABLE}")
        
        if not GPU_AVAILABLE:
            print("❌ GPU libraries not available")
            return False
        
        # Test if CUDA actually works
        import cupy as cp
        try:
            # Try to use GPU
            device = cp.cuda.Device(0)
            device.use()
            # Simple test
            test_array = cp.array([1, 2, 3])
            result = test_array.sum()
            print(f"✅ GPU test successful: {result}")
            return True
            
        except Exception as cuda_error:
            print(f"❌ CUDA Error: {cuda_error}")
            print("💡 GPU hardware available but drivers incompatible")
            print("💡 Google Colab free tier often has CUDA driver issues")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 GPU libraries not installed")
        return False

# Check GPU support
gpu_works = check_gpu_support()

if gpu_works:
    print("\n🎉 GPU acceleration available!")
    # Test with GPU
    try:
        from prime_checker.gpu_algorithms import is_prime_gpu
        result = is_prime_gpu(97)
        print(f"GPU prime test result: {result}")
    except Exception as e:
        print(f"GPU test failed: {e}")
        gpu_works = False

if not gpu_works:
    print("\n💻 Using CPU-only mode (recommended for Colab)")
    print("ℹ️  CPU algorithms are highly optimized and work great!")
```

### 2. Optimize for Colab Environment

```python
# Recommended settings for Colab
import os
os.environ['PYTHONUNBUFFERED'] = '1'  # Better progress display

# Use fewer rounds for faster testing in interactive environment
def quick_prime_test(n):
    """Quick prime test optimized for Colab."""
    return is_prime_cpu(n, algorithm='miller-rabin', rounds=5)

# Test with quick function
print("Quick tests:")
for num in [97, 101, 103, 107, 109]:
    print(f"{num}: {quick_prime_test(num)}")
```

### 3. Save Results

```python
# Save results to files in Colab
results = []

test_cases = [
    ("Small primes", [97, 101, 103]),
    ("Large primes", [1009, 10007, 100003]),
    ("Mersenne", [2**7-1, 2**13-1, 2**17-1])
]

for category, numbers in test_cases:
    print(f"\nTesting {category}:")
    for num in numbers:
        result = is_prime_cpu(num)
        results.append((category, num, result))
        print(f"  {num}: {'PRIME' if result else 'COMPOSITE'}")

# Save to file
with open('prime_test_results.txt', 'w') as f:
    for category, num, result in results:
        f.write(f"{category},{num},{'PRIME' if result else 'COMPOSITE'}\n")

print("\nResults saved to prime_test_results.txt")

# Download file (optional)
from google.colab import files
files.download('prime_test_results.txt')
```

## Troubleshooting

### Common Issues

1. **gmpy2 installation fails:**
```python
# Alternative installation
!apt-get update
!apt-get install -y libgmp-dev libmpfr-dev libmpc-dev
!pip install gmpy2
```

2. **GPU/CUDA errors (very common in Colab):**
```python
# Error: "CUDA driver version is insufficient"
# Solution: Use CPU-only mode (recommended)

# Force CPU-only mode
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Hide GPU from libraries

# Or just use CPU algorithms explicitly
from prime_checker.cpu_algorithms import is_prime_cpu
result = is_prime_cpu(97)  # Always works
```

3. **Memory issues with very large numbers:**
```python
# Use smaller test cases or fewer rounds
result = is_prime_cpu(large_number, algorithm='miller-rabin', rounds=3)
```

4. **Progress bars not displaying properly:**
```python
# Disable progress for cleaner output in Colab
result = is_prime_cpu(number, show_progress=False)
```

5. **CuPy installation issues:**
```python
# If you get CuPy errors, just skip GPU entirely
# The CPU algorithms are very fast and well-optimized

# Install without GPU dependencies
!pip install gmpy2 numpy click tqdm  # Skip cupy
```

### Performance Considerations

- **CPU Only**: Colab's free tier often has CUDA driver issues - CPU mode is recommended
- **CPU Performance**: The CPU algorithms are highly optimized with gmpy2 and very fast
- **Memory Limits**: Very large numbers (>10^10000 digits) may exceed memory limits  
- **Time Limits**: Long computations may timeout in Colab's free tier
- **GPU Reality**: Even with "GPU runtime", CUDA drivers often don't work properly

## Example Notebook Structure

```python
# Cell 1: Setup
!pip install gmpy2 numpy click tqdm
!git clone https://github.com/YOUR_USERNAME/prime_number.git
%cd prime_number
!pip install -e .

# Cell 2: Basic Tests
from prime_checker import is_prime_cpu
print("Basic functionality test:")
print(f"97 is prime: {is_prime_cpu(97)}")

# Cell 3: Mersenne Primes
print("Mersenne prime testing:")
for p in [7, 13, 17, 19]:
    Mp = 2**p - 1
    result = is_prime_cpu(Mp, algorithm='lucas-lehmer', p=p)
    print(f"M{p} = {Mp}: {'PRIME' if result else 'COMPOSITE'}")

# Cell 4: Large Number Generation
from prime_checker.utils import generate_random_probable_prime
print("Generated primes:")
for bits in [64, 128, 256]:
    prime = generate_random_probable_prime(bits)
    print(f"{bits}-bit: {prime}")
```

## Repository Setup

To use your own repository, replace the clone URL:

```python
# Replace with your actual repository URL
!git clone https://github.com/YOUR_USERNAME/prime_number.git
```

Or use the library directly if published to PyPI:

```python
# If published to PyPI (future)
!pip install prime-number-checker
```

This allows you to leverage Google Colab's computational resources for testing very large prime numbers without local setup requirements.