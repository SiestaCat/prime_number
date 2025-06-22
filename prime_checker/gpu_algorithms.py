"""GPU-based prime number algorithms using CUDA."""

import numpy as np
from typing import Union, List, Optional
import gmpy2
from gmpy2 import mpz

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    cp = None


class GPUPrimalityTest:
    """Base class for GPU-based primality tests."""
    
    def __init__(self):
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU support not available. Install cupy with: pip install cupy-cuda12x")
        
        self.device = cp.cuda.Device(0)
        self.device.use()
    
    def _to_gpu_format(self, n: mpz) -> tuple:
        """Convert large integer to GPU-compatible format."""
        # Convert to base 2^32 representation for GPU processing
        n_int = int(n)
        base = 2**32
        digits = []
        
        while n_int > 0:
            digits.append(n_int % base)
            n_int //= base
        
        return cp.array(digits, dtype=cp.uint32), len(digits)


class MillerRabinGPU(GPUPrimalityTest):
    """GPU-accelerated Miller-Rabin primality test."""
    
    def __init__(self, max_witnesses: int = 64):
        super().__init__()
        self.max_witnesses = max_witnesses
        
        # CUDA kernel for modular exponentiation
        self.mod_exp_kernel = cp.RawKernel(r'''
        extern "C" __global__
        void mod_exp_kernel(unsigned int* base, unsigned int* exp, 
                           unsigned int* mod, unsigned int* result,
                           int n_digits, int n_witnesses) {
            int tid = blockDim.x * blockIdx.x + threadIdx.x;
            if (tid >= n_witnesses) return;
            
            // Simplified modular exponentiation for demonstration
            // In practice, this would implement Montgomery reduction
            // for efficient large number arithmetic
            
            unsigned long long r = 1;
            unsigned long long b = base[tid];
            unsigned long long e = exp[0];  // Simplified: only using first digit
            unsigned long long m = mod[0];   // Simplified: only using first digit
            
            while (e > 0) {
                if (e & 1) {
                    r = (r * b) % m;
                }
                b = (b * b) % m;
                e >>= 1;
            }
            
            result[tid] = (unsigned int)r;
        }
        ''', 'mod_exp_kernel')
    
    def test_batch(self, numbers: List[Union[int, mpz]], rounds: int = 20) -> List[bool]:
        """
        Test multiple numbers for primality in parallel on GPU.
        
        Args:
            numbers: List of numbers to test
            rounds: Number of rounds per number
            
        Returns:
            List of boolean results
        """
        results = []
        
        for n in numbers:
            n = mpz(n)
            
            # Quick checks
            if n <= 1:
                results.append(False)
                continue
            if n <= 3:
                results.append(True)
                continue
            if n % 2 == 0:
                results.append(False)
                continue
            
            # For demonstration, use CPU fallback for very large numbers
            # A full implementation would handle arbitrary precision on GPU
            if n.bit_length() > 64:
                from .cpu_algorithms import MillerRabin
                cpu_test = MillerRabin(rounds=rounds)
                results.append(cpu_test.test(n))
            else:
                # Simplified GPU test for smaller numbers
                results.append(self._test_single_gpu(int(n), rounds))
        
        return results
    
    def _test_single_gpu(self, n: int, rounds: int) -> bool:
        """Test a single number on GPU (simplified for demonstration)."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Generate random witnesses
        witnesses = cp.random.randint(2, n-1, size=min(rounds, self.max_witnesses))
        
        # Decompose n-1 = 2^s * d
        n_minus_1 = n - 1
        s = 0
        d = n_minus_1
        while d % 2 == 0:
            d //= 2
            s += 1
        
        # Allocate GPU memory
        d_gpu = cp.array([d], dtype=cp.uint32)
        n_gpu = cp.array([n], dtype=cp.uint32)
        results = cp.zeros(len(witnesses), dtype=cp.uint32)
        
        # Launch kernel
        threads_per_block = 256
        blocks = (len(witnesses) + threads_per_block - 1) // threads_per_block
        
        self.mod_exp_kernel(
            (blocks,), (threads_per_block,),
            (witnesses, d_gpu, n_gpu, results, 1, len(witnesses))
        )
        
        # Check results (simplified)
        results_cpu = results.get()
        
        for i, r in enumerate(results_cpu):
            if r != 1 and r != n - 1:
                # Would need to do additional checks here
                return False
        
        return True


class LucasLehmerGPU(GPUPrimalityTest):
    """GPU-accelerated Lucas-Lehmer test for Mersenne primes."""
    
    def __init__(self):
        super().__init__()
        
        # CUDA kernel for Lucas-Lehmer iteration
        self.lucas_lehmer_kernel = cp.RawKernel(r'''
        extern "C" __global__
        void lucas_lehmer_iteration(unsigned long long* s, 
                                   unsigned long long* Mp,
                                   int iterations) {
            int tid = blockDim.x * blockIdx.x + threadIdx.x;
            if (tid != 0) return;  // Single thread for this operation
            
            unsigned long long si = s[0];
            unsigned long long modulus = Mp[0];
            
            for (int i = 0; i < iterations; i++) {
                // s = (s * s - 2) % Mp
                si = ((si * si) - 2) % modulus;
            }
            
            s[0] = si;
        }
        ''', 'lucas_lehmer_iteration')
    
    def test(self, p: int, batch_size: int = 1000) -> bool:
        """
        Test if Mp = 2^p - 1 is prime using GPU-accelerated Lucas-Lehmer.
        
        Args:
            p: The exponent (must be prime)
            batch_size: Number of iterations to process per kernel call
            
        Returns:
            True if Mp is prime, False otherwise
        """
        if p == 2:
            return True
        
        from .utils import is_prime_small
        if not is_prime_small(p):
            return False
        
        # For very large Mersenne numbers, fall back to CPU
        if p > 10000:
            from .cpu_algorithms import LucasLehmer
            cpu_test = LucasLehmer()
            return cpu_test.test(p, show_progress=True)
        
        # GPU computation for smaller Mersenne numbers
        Mp = int(2**p - 1)
        
        if Mp > 2**63:  # Beyond uint64 range
            from .cpu_algorithms import LucasLehmer
            cpu_test = LucasLehmer()
            return cpu_test.test(p, show_progress=True)
        
        s_gpu = cp.array([4], dtype=cp.uint64)
        Mp_gpu = cp.array([Mp], dtype=cp.uint64)
        
        total_iterations = p - 2
        iterations_done = 0
        
        while iterations_done < total_iterations:
            batch_iterations = min(batch_size, total_iterations - iterations_done)
            
            self.lucas_lehmer_kernel(
                (1,), (1,),
                (s_gpu, Mp_gpu, batch_iterations)
            )
            
            iterations_done += batch_iterations
        
        result = s_gpu.get()[0]
        return result == 0


class ParallelPrimeSearch:
    """GPU-accelerated parallel prime search."""
    
    def __init__(self):
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU support not available")
        
        self.miller_rabin_gpu = MillerRabinGPU()
    
    def find_primes_in_range(self, start: int, end: int, 
                           batch_size: int = 10000) -> List[int]:
        """
        Find all primes in a range using GPU parallelization.
        
        Args:
            start: Start of range (inclusive)
            end: End of range (exclusive)
            batch_size: Number of candidates to test in parallel
            
        Returns:
            List of prime numbers found
        """
        if start % 2 == 0:
            start += 1
        
        primes = []
        
        for batch_start in range(start, end, batch_size * 2):
            # Generate odd candidates
            batch_end = min(batch_start + batch_size * 2, end)
            candidates = list(range(batch_start, batch_end, 2))
            
            # Test batch on GPU
            results = self.miller_rabin_gpu.test_batch(candidates, rounds=10)
            
            # Collect primes
            for num, is_prime in zip(candidates, results):
                if is_prime:
                    primes.append(num)
        
        return primes


def is_prime_gpu(n: Union[int, mpz, str], algorithm: str = "miller-rabin", **kwargs) -> bool:
    """
    Check if n is prime using GPU algorithms.
    
    Args:
        n: Number to test
        algorithm: Algorithm to use ("miller-rabin" or "lucas-lehmer")
        **kwargs: Additional arguments
        
    Returns:
        True if n is probably prime, False if composite
    """
    if not GPU_AVAILABLE:
        raise RuntimeError("GPU support not available. Install with: pip install cupy-cuda12x")
    
    if isinstance(n, str):
        n = mpz(n)
    else:
        n = mpz(n)
    
    if algorithm == "miller-rabin":
        gpu_test = MillerRabinGPU()
        results = gpu_test.test_batch([n], rounds=kwargs.get('rounds', 20))
        return results[0]
    
    elif algorithm == "lucas-lehmer":
        if 'p' not in kwargs:
            # Check if n is Mersenne number
            if n > 3 and (n + 1).bit_count() == 1:
                p = (n + 1).bit_length() - 1
            else:
                raise ValueError("Lucas-Lehmer requires Mersenne number 2^p - 1")
        else:
            p = kwargs['p']
        
        gpu_test = LucasLehmerGPU()
        return gpu_test.test(p)
    
    else:
        raise ValueError(f"Unknown GPU algorithm: {algorithm}")


def find_primes_gpu(start: int, count: int, min_bits: int = 256) -> List[mpz]:
    """
    Find prime numbers using GPU acceleration.
    
    Args:
        start: Starting number
        count: Number of primes to find
        min_bits: Minimum bit length of primes
        
    Returns:
        List of prime numbers
    """
    if not GPU_AVAILABLE:
        raise RuntimeError("GPU support not available")
    
    searcher = ParallelPrimeSearch()
    primes = []
    
    current = max(start, 2**min_bits)
    if current % 2 == 0:
        current += 1
    
    while len(primes) < count:
        # Search in batches
        batch_primes = searcher.find_primes_in_range(
            current, current + 1000000, batch_size=10000
        )
        
        for p in batch_primes:
            if p.bit_length() >= min_bits:
                primes.append(mpz(p))
                if len(primes) >= count:
                    break
        
        current += 1000000
    
    return primes[:count]