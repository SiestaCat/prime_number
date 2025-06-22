"""Tests for CPU-based prime number algorithms."""

import pytest
from gmpy2 import mpz
from prime_checker.cpu_algorithms import (
    MillerRabin, LucasLehmer, LucasPrimality, BPSW, is_prime_cpu
)
from prime_checker.utils import generate_mersenne_candidate


class TestMillerRabin:
    """Test Miller-Rabin primality test."""
    
    def test_small_primes(self):
        """Test with small known primes."""
        mr = MillerRabin(rounds=10)
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        for p in small_primes:
            assert mr.test(p) is True
    
    def test_small_composites(self):
        """Test with small known composites."""
        mr = MillerRabin(rounds=10)
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        
        for c in composites:
            assert mr.test(c) is False
    
    def test_carmichael_numbers(self):
        """Test with Carmichael numbers (pseudoprimes)."""
        mr = MillerRabin(rounds=20)
        carmichael = [561, 1105, 1729, 2465, 2821, 6601, 8911]
        
        for c in carmichael:
            assert mr.test(c) is False
    
    def test_large_primes(self):
        """Test with known large primes."""
        mr = MillerRabin(rounds=5)
        
        # Some known Mersenne primes
        mersenne_exponents = [2, 3, 5, 7, 13, 17, 19, 31]
        for p in mersenne_exponents:
            Mp = generate_mersenne_candidate(p)
            assert mr.test(Mp) is True
    
    def test_deterministic_mode(self):
        """Test deterministic mode for smaller numbers."""
        mr = MillerRabin()
        
        # Test primes
        primes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139]
        for p in primes:
            assert mr.test(p, use_deterministic=True) is True
        
        # Test composites
        composites = [91, 121, 143, 169, 187, 209, 221, 247, 253, 289]
        for c in composites:
            assert mr.test(c, use_deterministic=True) is False


class TestLucasLehmer:
    """Test Lucas-Lehmer test for Mersenne primes."""
    
    def test_known_mersenne_primes(self):
        """Test with known Mersenne prime exponents."""
        ll = LucasLehmer()
        
        # First few Mersenne prime exponents
        mersenne_prime_exponents = [2, 3, 5, 7, 13, 17, 19, 31]
        
        for p in mersenne_prime_exponents:
            assert ll.test(p, show_progress=False) is True
    
    def test_non_mersenne_exponents(self):
        """Test with exponents that don't produce Mersenne primes."""
        ll = LucasLehmer()
        
        # Known non-Mersenne prime exponents
        non_mersenne = [11, 23, 29, 37, 41, 43, 47, 53, 59]
        
        for p in non_mersenne:
            assert ll.test(p, show_progress=False) is False
    
    def test_composite_exponents(self):
        """Test that composite exponents are rejected."""
        ll = LucasLehmer()
        
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in composites:
            assert ll.test(c, show_progress=False) is False


class TestLucasPrimality:
    """Test Lucas primality test."""
    
    def test_small_primes(self):
        """Test with small primes."""
        lucas = LucasPrimality()
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        for p in primes:
            assert lucas.test(p) is True
    
    def test_small_composites(self):
        """Test with small composites."""
        lucas = LucasPrimality()
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        
        for c in composites:
            assert lucas.test(c) is False


class TestBPSW:
    """Test Baillie-PSW primality test."""
    
    def test_no_known_counterexamples(self):
        """Test that BPSW correctly identifies primes and composites."""
        bpsw = BPSW()
        
        # Test primes
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97, 101, 103, 107, 109]
        for p in primes:
            assert bpsw.test(p) is True
        
        # Test composites
        composites = [4, 6, 8, 9, 10, 91, 121, 143, 169, 187]
        for c in composites:
            assert bpsw.test(c) is False
    
    def test_pseudoprimes(self):
        """Test with numbers that fool other tests."""
        bpsw = BPSW()
        
        # Strong pseudoprimes to various bases
        pseudoprimes = [341, 561, 645, 1105, 1387, 1729, 1905]
        for pp in pseudoprimes:
            assert bpsw.test(pp) is False


class TestIsPrimeCPU:
    """Test the main is_prime_cpu function."""
    
    def test_auto_algorithm_selection(self):
        """Test automatic algorithm selection."""
        # Mersenne number should use Lucas-Lehmer
        M7 = generate_mersenne_candidate(7)  # 127
        assert is_prime_cpu(M7, algorithm="auto") is True
        
        # Regular number should use BPSW
        assert is_prime_cpu(97, algorithm="auto") is True
        assert is_prime_cpu(98, algorithm="auto") is False
    
    def test_string_input(self):
        """Test with string input."""
        assert is_prime_cpu("97") is True
        assert is_prime_cpu("100") is False
        assert is_prime_cpu("1000000007") is True
    
    def test_specific_algorithms(self):
        """Test specific algorithm selection."""
        # Miller-Rabin
        assert is_prime_cpu(97, algorithm="miller-rabin", rounds=10) is True
        
        # Lucas-Lehmer for Mersenne
        assert is_prime_cpu(127, algorithm="lucas-lehmer", p=7) is True
        
        # BPSW
        assert is_prime_cpu(97, algorithm="bpsw") is True
    
    def test_very_large_numbers(self):
        """Test with very large numbers."""
        # Large prime (Mersenne M61)
        large_prime = mpz(2)**61 - 1
        assert is_prime_cpu(large_prime, algorithm="bpsw") is True
        
        # Large composite
        large_composite = mpz(2)**60 - 1  # Divisible by 3
        assert is_prime_cpu(large_composite, algorithm="bpsw") is False
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert is_prime_cpu(0) is False
        assert is_prime_cpu(1) is False
        assert is_prime_cpu(2) is True
        assert is_prime_cpu(-5) is False