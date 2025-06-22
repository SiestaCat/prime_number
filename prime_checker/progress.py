"""Progress tracking utilities for prime number computations."""

import time
import sys
from typing import Optional, Callable, Any
from tqdm import tqdm


class ProgressTracker:
    """Enhanced progress tracker with time estimation."""
    
    def __init__(self, total_iterations: int, description: str = "Processing"):
        self.total_iterations = total_iterations
        self.description = description
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.current_iteration = 0
        self.update_interval = max(1, total_iterations // 1000)  # Update every 0.1%
        
        # Initialize tqdm progress bar
        self.pbar = tqdm(
            total=total_iterations,
            desc=description,
            unit="iter",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {percentage:.2f}%"
        )
    
    def update(self, iterations: int = 1):
        """Update progress by specified number of iterations."""
        self.current_iteration += iterations
        current_time = time.time()
        
        # Update tqdm
        self.pbar.update(iterations)
        
        # Update custom stats
        if (self.current_iteration % self.update_interval == 0 or 
            self.current_iteration >= self.total_iterations):
            
            elapsed_time = current_time - self.start_time
            progress_ratio = self.current_iteration / self.total_iterations
            
            if progress_ratio > 0:
                estimated_total_time = elapsed_time / progress_ratio
                remaining_time = estimated_total_time - elapsed_time
                
                # Update tqdm description with custom format
                percentage = progress_ratio * 100
                self.pbar.set_description(
                    f"{self.description} ({percentage:.2f}%)"
                )
    
    def close(self):
        """Close the progress bar."""
        self.pbar.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LucasLehmerProgress:
    """Specialized progress tracker for Lucas-Lehmer test."""
    
    def __init__(self, p: int, show_progress: bool = True):
        self.p = p
        self.total_iterations = p - 2
        self.show_progress = show_progress
        self.tracker = None
        
        if show_progress and self.total_iterations > 10:
            self.tracker = ProgressTracker(
                self.total_iterations,
                f"Lucas-Lehmer M{p}"
            )
    
    def update(self, iterations: int = 1):
        """Update progress."""
        if self.tracker:
            self.tracker.update(iterations)
    
    def close(self):
        """Close progress tracker."""
        if self.tracker:
            self.tracker.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MillerRabinProgress:
    """Progress tracker for Miller-Rabin test rounds."""
    
    def __init__(self, rounds: int, number_bit_length: int, show_progress: bool = True):
        self.rounds = rounds
        self.number_bit_length = number_bit_length
        self.show_progress = show_progress
        self.tracker = None
        
        # Only show progress for large numbers or many rounds
        if show_progress and (rounds > 20 or number_bit_length > 1000):
            self.tracker = ProgressTracker(
                rounds,
                f"Miller-Rabin ({number_bit_length} bits)"
            )
    
    def update(self, iterations: int = 1):
        """Update progress."""
        if self.tracker:
            self.tracker.update(iterations)
    
    def close(self):
        """Close progress tracker."""
        if self.tracker:
            self.tracker.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BatchProgress:
    """Progress tracker for batch operations."""
    
    def __init__(self, total_numbers: int, operation: str = "Testing"):
        self.total_numbers = total_numbers
        self.operation = operation
        self.tracker = ProgressTracker(
            total_numbers,
            f"{operation} primes"
        )
        
        self.results = {"prime": 0, "composite": 0, "error": 0}
    
    def update_result(self, result: str):
        """Update with result type and progress."""
        if result in self.results:
            self.results[result] += 1
        
        total_processed = sum(self.results.values())
        prime_count = self.results["prime"]
        
        # Update description with results
        self.tracker.pbar.set_description(
            f"{self.operation} (Primes: {prime_count}/{total_processed})"
        )
        self.tracker.update(1)
    
    def close(self):
        """Close progress tracker."""
        self.tracker.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def with_progress(func: Callable, total_steps: int, description: str = "Processing"):
    """Decorator to add progress tracking to a function."""
    def wrapper(*args, **kwargs):
        show_progress = kwargs.pop('show_progress', True)
        
        if not show_progress:
            return func(*args, **kwargs)
        
        with ProgressTracker(total_steps, description) as tracker:
            # Pass tracker to function if it accepts it
            try:
                return func(*args, progress_tracker=tracker, **kwargs)
            except TypeError:
                # Function doesn't accept progress_tracker parameter
                return func(*args, **kwargs)
    
    return wrapper


class GenerationProgress:
    """Progress tracker for prime generation."""
    
    def __init__(self, target_count: int, bits: int, mode: str = "random"):
        self.target_count = target_count
        self.bits = bits
        self.mode = mode
        self.found_count = 0
        self.tested_count = 0
        
        # Estimate total candidates to test based on prime number theorem
        if mode == "mersenne":
            estimated_tests = target_count * 10  # Rough estimate for Mersenne
        else:
            # Prime number theorem: π(n) ≈ n/ln(n)
            import math
            n = 2**bits
            estimated_density = math.log(n)
            estimated_tests = int(target_count * estimated_density * 1.5)  # Add safety margin
        
        self.tracker = ProgressTracker(
            estimated_tests,
            f"Generating {target_count} {bits}-bit primes"
        )
    
    def update_tested(self, is_prime: bool = False):
        """Update when a candidate is tested."""
        self.tested_count += 1
        if is_prime:
            self.found_count += 1
        
        # Update description
        percentage = (self.found_count / self.target_count) * 100
        self.tracker.pbar.set_description(
            f"Found {self.found_count}/{self.target_count} primes ({percentage:.2f}%)"
        )
        
        # Update progress (but don't exceed total)
        if self.tracker.current_iteration < self.tracker.total_iterations:
            self.tracker.update(1)
    
    def close(self):
        """Close progress tracker."""
        self.tracker.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()