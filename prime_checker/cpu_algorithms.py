"""CPU-based prime number algorithms for very large numbers."""

import gmpy2
from gmpy2 import mpz
import random
from typing import List, Optional, Union
from tqdm import tqdm
from .utils import mod_exp, decompose_n_minus_1, jacobi_symbol, is_prime_small


class MillerRabin:
    """Miller-Rabin primality test implementation."""
    
    def __init__(self, rounds: int = 20):
        self.rounds = rounds
        # Deterministic bases for numbers < 3,317,044,064,679,887,385,961,981
        self.deterministic_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    def test(self, n: Union[int, mpz], use_deterministic: bool = False) -> bool:
        """
        Test if n is prime using Miller-Rabin algorithm.
        
        Args:
            n: Number to test
            use_deterministic: Use deterministic bases for smaller numbers
            
        Returns:
            True if n is probably prime, False if composite
        """
        n = mpz(n)
        
        # Handle small cases
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False
        
        # For small numbers, use simple primality test
        if n < 2**64:
            return is_prime_small(int(n))
        
        # Decompose n-1 = 2^s * d
        s, d = decompose_n_minus_1(n)
        
        # Choose witnesses
        if use_deterministic and n < mpz(3317044064679887385961981):
            witnesses = [a for a in self.deterministic_bases if a < n]
        else:
            witnesses = [mpz(random.randrange(2, int(n - 1))) for _ in range(self.rounds)]
        
        # Run Miller-Rabin test
        for a in witnesses:
            if not self._witness_test(a, n, s, d):
                return False
        
        return True
    
    def _witness_test(self, a: mpz, n: mpz, s: mpz, d: mpz) -> bool:
        """Test if a is a witness for the compositeness of n."""
        x = mod_exp(a, d, n)
        
        if x == 1 or x == n - 1:
            return True
        
        for _ in range(int(s) - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                return True
            if x == 1:
                return False
        
        return False


class LucasLehmer:
    """Lucas-Lehmer test for Mersenne primes."""
    
    def test(self, p: int, show_progress: bool = True) -> bool:
        """
        Test if Mp = 2^p - 1 is prime using Lucas-Lehmer test.
        
        Args:
            p: The exponent (must be prime)
            show_progress: Show progress bar
            
        Returns:
            True if Mp is prime, False otherwise
        """
        if p == 2:
            return True
        
        if not is_prime_small(p):
            return False
        
        Mp = mpz(2)**p - 1
        s = mpz(4)
        
        iterator = range(p - 2)
        if show_progress and p > 1000:
            iterator = tqdm(iterator, desc=f"Testing M{p}")
        
        for _ in iterator:
            s = (s * s - 2) % Mp
        
        return s == 0


class LucasPrimality:
    """Lucas primality test for general numbers."""
    
    def test(self, n: Union[int, mpz]) -> bool:
        """
        Test if n is prime using Lucas sequences.
        
        Args:
            n: Number to test
            
        Returns:
            True if n is probably prime, False if composite
        """
        n = mpz(n)
        
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Find D such that jacobi(D, n) = -1
        D = self._find_D(n)
        if D is None:
            return False
        
        # Compute Lucas sequence
        return self._lucas_sequence_test(n, D)
    
    def _find_D(self, n: mpz) -> Optional[mpz]:
        """Find D such that jacobi(D, n) = -1."""
        D = mpz(5)
        while True:
            if jacobi_symbol(D, n) == -1:
                return D
            
            if D > 0:
                D = -D - 2
            else:
                D = -D + 2
            
            if abs(D) > n:
                return None
    
    def _lucas_sequence_test(self, n: mpz, D: mpz) -> bool:
        """Perform Lucas sequence test."""
        P = mpz(1)
        Q = (1 - D) // 4
        
        # Compute U_{n+1} mod n
        k = n + 1
        U = mpz(0)
        V = mpz(2)
        Qk = mpz(1)
        
        for bit in bin(k)[2:]:
            U = U * V % n
            V = (V * V - 2 * Qk) % n
            Qk = Qk * Qk % n
            
            if bit == '1':
                U, V = (P * U + V) // 2 % n, (D * U + P * V) // 2 % n
                Qk = Qk * Q % n
        
        return U == 0


class BPSW:
    """Baillie-PSW primality test combining Miller-Rabin and Lucas tests."""
    
    def __init__(self):
        self.miller_rabin = MillerRabin(rounds=1)
        self.lucas = LucasPrimality()
    
    def test(self, n: Union[int, mpz]) -> bool:
        """
        Test if n is prime using BPSW algorithm.
        No known composite numbers pass this test.
        
        Args:
            n: Number to test
            
        Returns:
            True if n is probably prime, False if composite
        """
        n = mpz(n)
        
        # Quick checks
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Miller-Rabin test with base 2
        if not self.miller_rabin.test(n, use_deterministic=True):
            return False
        
        # Lucas test
        return self.lucas.test(n)


def is_prime_cpu(n: Union[int, mpz, str], algorithm: str = "auto", **kwargs) -> bool:
    """
    Check if n is prime using CPU algorithms.
    
    Args:
        n: Number to test (can be int, mpz, or string)
        algorithm: Algorithm to use ("miller-rabin", "lucas-lehmer", "bpsw", or "auto")
        **kwargs: Additional arguments for specific algorithms
        
    Returns:
        True if n is probably prime, False if composite
    """
    if isinstance(n, str):
        n = mpz(n)
    else:
        n = mpz(n)
    
    if algorithm == "auto":
        # Check if it's a Mersenne number
        if n > 3 and (n + 1).bit_count() == 1:
            p = (n + 1).bit_length() - 1
            if is_prime_small(p):
                algorithm = "lucas-lehmer"
                kwargs['p'] = p
        else:
            algorithm = "bpsw"
    
    if algorithm == "miller-rabin":
        rounds = kwargs.get('rounds', 20)
        mr = MillerRabin(rounds=rounds)
        return mr.test(n)
    
    elif algorithm == "lucas-lehmer":
        if 'p' not in kwargs:
            raise ValueError("Lucas-Lehmer requires exponent p for testing 2^p - 1")
        ll = LucasLehmer()
        return ll.test(kwargs['p'], show_progress=kwargs.get('show_progress', True))
    
    elif algorithm == "bpsw":
        bpsw = BPSW()
        return bpsw.test(n)
    
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")