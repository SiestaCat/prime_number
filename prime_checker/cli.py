"""Command-line interface for prime number checker."""

import click
import sys
import time
from pathlib import Path
import gmpy2
from gmpy2 import mpz
from .cpu_algorithms import is_prime_cpu
from .utils import generate_random_probable_prime, generate_mersenne_candidate
from .progress import BatchProgress, GenerationProgress

try:
    from .gpu_algorithms import is_prime_gpu, find_primes_gpu, GPU_AVAILABLE
except ImportError:
    GPU_AVAILABLE = False
    is_prime_gpu = None
    find_primes_gpu = None


@click.group()
@click.version_option(version='1.0.0')
def main():
    """High-performance prime number checker for very large numbers."""
    pass


@main.command()
@click.argument('number', type=str)
@click.option('--algorithm', '-a', type=click.Choice(['auto', 'miller-rabin', 'lucas-lehmer', 'bpsw']), 
              default='auto', help='Algorithm to use')
@click.option('--rounds', '-r', type=int, default=20, help='Number of rounds for Miller-Rabin')
@click.option('--use-gpu', '-g', is_flag=True, help='Use GPU acceleration if available')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def check(number, algorithm, rounds, use_gpu, verbose):
    """Check if a number is prime."""
    try:
        # Parse the number
        if number.startswith('2^') and '-1' in number:
            # Mersenne number format: 2^p-1
            p = int(number[2:number.index('-1')])
            n = generate_mersenne_candidate(p)
            if verbose:
                click.echo(f"Testing Mersenne number M{p} = 2^{p} - 1")
                click.echo(f"Number has {len(str(n))} decimal digits")
        elif '^' in number:
            # Exponential format: base^exp
            base, exp = number.split('^')
            n = mpz(int(base)) ** int(exp)
        else:
            # Regular number or expression
            n = mpz(eval(number))
        
        # Choose computation method
        if use_gpu and GPU_AVAILABLE:
            if verbose:
                click.echo("Using GPU acceleration...")
            start_time = time.time()
            
            # Special handling for Mersenne numbers
            if algorithm == 'auto' and number.startswith('2^') and '-1' in number:
                is_prime = is_prime_gpu(n, algorithm='lucas-lehmer', p=p)
            else:
                is_prime = is_prime_gpu(n, algorithm=algorithm, rounds=rounds)
        else:
            if use_gpu and not GPU_AVAILABLE:
                click.echo("Warning: GPU requested but not available. Using CPU.", err=True)
            
            if verbose:
                click.echo("Using CPU computation...")
            start_time = time.time()
            
            # Special handling for Mersenne numbers
            if algorithm == 'auto' and number.startswith('2^') and '-1' in number:
                is_prime = is_prime_cpu(n, algorithm='lucas-lehmer', p=p, show_progress=verbose)
            else:
                is_prime = is_prime_cpu(n, algorithm=algorithm, rounds=rounds, show_progress=verbose)
        
        elapsed_time = time.time() - start_time
        
        # Output results
        if verbose:
            click.echo(f"\nComputation time: {elapsed_time:.3f} seconds")
            click.echo(f"Number of digits: {len(str(n))}")
            click.echo(f"Number of bits: {n.bit_length()}")
        
        if is_prime:
            click.echo(click.style("PRIME", fg='green', bold=True))
        else:
            click.echo(click.style("COMPOSITE", fg='red', bold=True))
        
        sys.exit(0 if is_prime else 1)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)


@main.command()
@click.option('--bits', '-b', type=int, default=256, help='Bit length of the prime')
@click.option('--count', '-c', type=int, default=1, help='Number of primes to generate')
@click.option('--mersenne', '-m', is_flag=True, help='Generate Mersenne prime candidates')
@click.option('--use-gpu', '-g', is_flag=True, help='Use GPU acceleration if available')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def generate(bits, count, mersenne, use_gpu, output):
    """Generate random probable prime numbers."""
    primes = []
    
    if mersenne:
        click.echo(f"Generating {count} Mersenne prime candidates...")
        # Find prime exponents first
        p = 2
        while len(primes) < count:
            p = int(generate_random_probable_prime(max(7, bits // 100)))
            Mp = generate_mersenne_candidate(p)
            if Mp.bit_length() >= bits:
                primes.append((p, Mp))
                click.echo(f"Generated M{p} = 2^{p} - 1 ({len(str(Mp))} digits)")
    else:
        if use_gpu and GPU_AVAILABLE and find_primes_gpu:
            click.echo(f"Generating {count} {bits}-bit primes using GPU...")
            prime_list = find_primes_gpu(2**bits, count, min_bits=bits)
            for p in prime_list:
                primes.append(p)
                click.echo(f"Generated: {str(p)[:50]}... ({p.bit_length()} bits)")
        else:
            with GenerationProgress(count, bits, "random") as progress:
                for i in range(count):
                    p = generate_random_probable_prime(bits)
                    primes.append(p)
                    progress.update_tested(is_prime=True)
                    click.echo(f"Generated: {str(p)[:50]}... ({p.bit_length()} bits)")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            for p in primes:
                if isinstance(p, tuple):  # Mersenne format
                    f.write(f"2^{p[0]}-1\n")
                else:
                    f.write(f"{p}\n")
        click.echo(f"Saved {len(primes)} primes to {output}")


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--algorithm', '-a', type=click.Choice(['auto', 'miller-rabin', 'lucas-lehmer', 'bpsw']), 
              default='auto', help='Algorithm to use')
@click.option('--use-gpu', '-g', is_flag=True, help='Use GPU acceleration if available')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch(input_file, algorithm, use_gpu, output, verbose):
    """Check multiple numbers from a file."""
    results = []
    
    with open(input_file, 'r') as f:
        numbers = [line.strip() for line in f if line.strip()]
    
    with BatchProgress(len(numbers), "Testing") as progress:
        for i, number_str in enumerate(numbers):
            if verbose:
                click.echo(f"\nTesting number {i+1}/{len(numbers)}: {number_str[:50]}...")
            
            try:
                # Parse number (similar to check command)
                if number_str.startswith('2^') and '-1' in number_str:
                    p = int(number_str[2:number_str.index('-1')])
                    n = generate_mersenne_candidate(p)
                else:
                    n = mpz(number_str)
                
                # Test primality
                if use_gpu and GPU_AVAILABLE:
                    is_prime = is_prime_gpu(n, algorithm=algorithm)
                else:
                    is_prime = is_prime_cpu(n, algorithm=algorithm, show_progress=False)  # Don't show individual progress in batch
                
                results.append((number_str, is_prime))
                
                # Update progress
                if is_prime:
                    progress.update_result("prime")
                else:
                    progress.update_result("composite")
                
                if verbose:
                    status = "PRIME" if is_prime else "COMPOSITE"
                    color = 'green' if is_prime else 'red'
                    click.echo(click.style(status, fg=color))
                    
            except Exception as e:
                results.append((number_str, f"ERROR: {str(e)}"))
                progress.update_result("error")
                if verbose:
                    click.echo(click.style(f"ERROR: {str(e)}", fg='yellow'))
    
    # Summary
    prime_count = sum(1 for _, result in results if result is True)
    composite_count = sum(1 for _, result in results if result is False)
    error_count = sum(1 for _, result in results if isinstance(result, str))
    
    click.echo(f"\nSummary:")
    click.echo(f"  Prime: {prime_count}")
    click.echo(f"  Composite: {composite_count}")
    click.echo(f"  Errors: {error_count}")
    
    # Save results if requested
    if output:
        with open(output, 'w') as f:
            for number, result in results:
                if isinstance(result, bool):
                    status = "PRIME" if result else "COMPOSITE"
                else:
                    status = result
                f.write(f"{number}\t{status}\n")
        click.echo(f"\nResults saved to {output}")


@main.command()
def info():
    """Display system information."""
    click.echo("Prime Number Checker v1.0.0")
    click.echo(f"GPU Support: {'Available' if GPU_AVAILABLE else 'Not available'}")
    
    if GPU_AVAILABLE:
        import cupy as cp
        click.echo(f"CUDA Version: {cp.cuda.runtime.runtimeGetVersion()}")
        click.echo(f"GPU Device: {cp.cuda.Device(0).name.decode()}")
        click.echo(f"GPU Memory: {cp.cuda.Device(0).mem_info[1] / 1e9:.1f} GB")
    
    click.echo(f"\nMax integer precision: Unlimited (using gmpy2)")
    click.echo("Supported algorithms:")
    click.echo("  - Miller-Rabin (CPU/GPU)")
    click.echo("  - Lucas-Lehmer (CPU/GPU)")
    click.echo("  - Baillie-PSW (CPU)")
    click.echo("  - Lucas Primality Test (CPU)")


if __name__ == '__main__':
    main()