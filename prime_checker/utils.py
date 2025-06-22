"""Utility functions for prime number operations."""

import gmpy2
from gmpy2 import mpz
import random
from typing import Union, Tuple


def mod_exp(base: mpz, exp: mpz, mod: mpz) -> mpz:
    """Fast modular exponentiation using gmpy2."""
    return gmpy2.powmod(base, exp, mod)


def is_probably_prime(n: mpz, k: int = 20) -> bool:
    """Quick probabilistic primality test using gmpy2."""
    return gmpy2.is_prime(n, k)


def generate_random_probable_prime(bits: int) -> mpz:
    """Generate a random probable prime with specified bit length."""
    while True:
        n = mpz(2)**(bits - 1) + mpz(random.getrandbits(bits - 1))
        if n % 2 == 0:
            n += 1
        
        if is_probably_prime(n, 5):
            return n


def jacobi_symbol(a: mpz, n: mpz) -> int:
    """Compute the Jacobi symbol (a/n)."""
    return gmpy2.jacobi(a, n)


def is_perfect_square(n: mpz) -> Tuple[bool, mpz]:
    """Check if n is a perfect square and return the square root if it is."""
    sqrt_n = gmpy2.isqrt(n)
    return (sqrt_n * sqrt_n == n, sqrt_n)


def generate_mersenne_candidate(p: int) -> mpz:
    """Generate Mersenne number 2^p - 1."""
    return mpz(2)**p - 1


def decompose_n_minus_1(n: mpz) -> Tuple[mpz, mpz]:
    """Decompose n-1 as 2^s * d where d is odd."""
    n_minus_1 = n - 1
    s = mpz(0)
    d = n_minus_1
    
    while d % 2 == 0:
        d //= 2
        s += 1
    
    return s, d


def is_prime_small(n: int) -> bool:
    """Check primality for small numbers < 2^64."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Use trial division for very small numbers
    if n < 1000:
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # Use gmpy2 for larger small numbers
    return gmpy2.is_prime(n)