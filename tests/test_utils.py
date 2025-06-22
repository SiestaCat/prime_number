"""Tests for utility functions."""

import pytest
from gmpy2 import mpz
from prime_checker.utils import (
    mod_exp, is_probably_prime, generate_random_probable_prime,
    jacobi_symbol, is_perfect_square, generate_mersenne_candidate,
    decompose_n_minus_1, is_prime_small
)


class TestModExp:
    """Test modular exponentiation."""
    
    def test_basic_cases(self):
        """Test basic modular exponentiation."""
        assert mod_exp(mpz(2), mpz(3), mpz(5)) == 3  # 2^3 % 5 = 8 % 5 = 3
        assert mod_exp(mpz(3), mpz(4), mpz(7)) == 4  # 3^4 % 7 = 81 % 7 = 4
        assert mod_exp(mpz(5), mpz(3), mpz(13)) == 8  # 5^3 % 13 = 125 % 13 = 8
    
    def test_large_exponents(self):
        """Test with large exponents."""
        # Fermat's little theorem: a^(p-1) ≡ 1 (mod p) for prime p
        assert mod_exp(mpz(2), mpz(10), mpz(11)) == 1  # 2^10 % 11 = 1
        assert mod_exp(mpz(3), mpz(6), mpz(7)) == 1    # 3^6 % 7 = 1
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert mod_exp(mpz(0), mpz(5), mpz(7)) == 0
        assert mod_exp(mpz(5), mpz(0), mpz(7)) == 1
        assert mod_exp(mpz(1), mpz(100), mpz(7)) == 1


class TestIsProbablyPrime:
    """Test probabilistic primality testing."""
    
    def test_small_primes(self):
        """Test with small primes."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for p in primes:
            assert is_probably_prime(mpz(p), k=5) is True
    
    def test_small_composites(self):
        """Test with small composites."""
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        for c in composites:
            assert is_probably_prime(mpz(c), k=5) is False


class TestGenerateRandomProbablePrime:
    """Test random prime generation."""
    
    def test_bit_length(self):
        """Test that generated primes have correct bit length."""
        for bits in [8, 16, 32, 64, 128]:
            p = generate_random_probable_prime(bits)
            assert p.bit_length() == bits
            assert is_probably_prime(p, k=10) is True
    
    def test_multiple_generations(self):
        """Test that different primes are generated."""
        primes = set()
        for _ in range(10):
            p = generate_random_probable_prime(16)
            primes.add(int(p))
        
        # Should generate different primes (very unlikely to get duplicates)
        assert len(primes) > 5


class TestJacobiSymbol:
    """Test Jacobi symbol computation."""
    
    def test_known_values(self):
        """Test with known Jacobi symbol values."""
        # (a/n) values
        assert jacobi_symbol(mpz(2), mpz(3)) == -1
        assert jacobi_symbol(mpz(2), mpz(5)) == -1
        assert jacobi_symbol(mpz(2), mpz(7)) == 1
        assert jacobi_symbol(mpz(3), mpz(5)) == -1
        assert jacobi_symbol(mpz(3), mpz(7)) == -1
        assert jacobi_symbol(mpz(5), mpz(7)) == -1
    
    def test_properties(self):
        """Test Jacobi symbol properties."""
        # (a/n) = 0 if gcd(a,n) > 1
        assert jacobi_symbol(mpz(6), mpz(9)) == 0
        assert jacobi_symbol(mpz(10), mpz(15)) == 0
        
        # (1/n) = 1 for all odd n
        for n in [3, 5, 7, 9, 11, 13, 15]:
            assert jacobi_symbol(mpz(1), mpz(n)) == 1


class TestIsPerfectSquare:
    """Test perfect square detection."""
    
    def test_perfect_squares(self):
        """Test with perfect squares."""
        squares = [(0, 0), (1, 1), (4, 2), (9, 3), (16, 4), (25, 5), 
                  (36, 6), (49, 7), (64, 8), (81, 9), (100, 10)]
        
        for square, root in squares:
            is_square, sqrt_n = is_perfect_square(mpz(square))
            assert is_square is True
            assert sqrt_n == root
    
    def test_non_squares(self):
        """Test with non-perfect squares."""
        non_squares = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15]
        
        for n in non_squares:
            is_square, _ = is_perfect_square(mpz(n))
            assert is_square is False
    
    def test_large_squares(self):
        """Test with large perfect squares."""
        large_root = mpz(12345678901234567890)
        large_square = large_root * large_root
        
        is_square, sqrt_n = is_perfect_square(large_square)
        assert is_square is True
        assert sqrt_n == large_root


class TestGenerateMersenneCandidate:
    """Test Mersenne number generation."""
    
    def test_small_mersenne(self):
        """Test generation of small Mersenne numbers."""
        assert generate_mersenne_candidate(2) == 3    # 2^2 - 1 = 3
        assert generate_mersenne_candidate(3) == 7    # 2^3 - 1 = 7
        assert generate_mersenne_candidate(5) == 31   # 2^5 - 1 = 31
        assert generate_mersenne_candidate(7) == 127  # 2^7 - 1 = 127
    
    def test_bit_length(self):
        """Test bit length of Mersenne numbers."""
        for p in [10, 20, 30, 40, 50]:
            Mp = generate_mersenne_candidate(p)
            assert Mp.bit_length() == p


class TestDecomposeNMinus1:
    """Test decomposition of n-1."""
    
    def test_decomposition(self):
        """Test n-1 = 2^s * d decomposition."""
        test_cases = [
            (mpz(9), mpz(3), mpz(1)),    # 8 = 2^3 * 1
            (mpz(17), mpz(4), mpz(1)),   # 16 = 2^4 * 1
            (mpz(25), mpz(3), mpz(3)),   # 24 = 2^3 * 3
            (mpz(49), mpz(4), mpz(3)),   # 48 = 2^4 * 3
            (mpz(101), mpz(2), mpz(25)), # 100 = 2^2 * 25
        ]
        
        for n, expected_s, expected_d in test_cases:
            s, d = decompose_n_minus_1(n)
            assert s == expected_s
            assert d == expected_d
            assert n - 1 == (2**s) * d
    
    def test_odd_n_minus_1(self):
        """Test when n-1 is odd (n=2)."""
        s, d = decompose_n_minus_1(mpz(2))
        assert s == 0
        assert d == 1


class TestIsPrimeSmall:
    """Test primality testing for small numbers."""
    
    def test_small_primes(self):
        """Test small prime numbers."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
        
        for p in primes:
            assert is_prime_small(p) is True
    
    def test_small_composites(self):
        """Test small composite numbers."""
        composites = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22,
                     24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36, 38, 39, 40]
        
        for c in composites:
            assert is_prime_small(c) is False
    
    def test_negative_numbers(self):
        """Test negative numbers."""
        assert is_prime_small(-1) is False
        assert is_prime_small(-2) is False
        assert is_prime_small(-5) is False