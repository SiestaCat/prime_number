"""Tests for progress tracking system."""

import pytest
import time
from unittest.mock import patch, MagicMock
from prime_checker.progress import (
    ProgressTracker, LucasLehmerProgress, MillerRabinProgress,
    BatchProgress, GenerationProgress
)


class TestProgressTracker:
    """Test basic progress tracker functionality."""
    
    def test_init(self):
        """Test progress tracker initialization."""
        tracker = ProgressTracker(100, "Test")
        assert tracker.total_iterations == 100
        assert tracker.description == "Test"
        assert tracker.current_iteration == 0
    
    def test_update(self):
        """Test progress updates."""
        with ProgressTracker(10, "Test") as tracker:
            tracker.update(5)
            assert tracker.current_iteration == 5
            
            tracker.update(3)
            assert tracker.current_iteration == 8
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with ProgressTracker(10, "Test") as tracker:
            assert tracker is not None
            tracker.update(5)
        # Should close without errors


class TestLucasLehmerProgress:
    """Test Lucas-Lehmer progress tracker."""
    
    def test_small_p_no_progress(self):
        """Test that small p values don't show progress."""
        with LucasLehmerProgress(5, show_progress=True) as progress:
            assert progress.tracker is None
    
    def test_large_p_with_progress(self):
        """Test that large p values show progress."""
        with LucasLehmerProgress(100, show_progress=True) as progress:
            assert progress.tracker is not None
            assert progress.total_iterations == 98  # p - 2
    
    def test_no_progress_flag(self):
        """Test show_progress=False."""
        with LucasLehmerProgress(100, show_progress=False) as progress:
            assert progress.tracker is None
    
    def test_update(self):
        """Test progress updates."""
        with LucasLehmerProgress(50, show_progress=True) as progress:
            if progress.tracker:  # Only test if progress is shown
                progress.update(10)
                assert progress.tracker.current_iteration == 10


class TestMillerRabinProgress:
    """Test Miller-Rabin progress tracker."""
    
    def test_small_numbers_no_progress(self):
        """Test small numbers don't show progress."""
        with MillerRabinProgress(10, 500, show_progress=True) as progress:
            assert progress.tracker is None
    
    def test_large_numbers_with_progress(self):
        """Test large numbers show progress."""
        with MillerRabinProgress(50, 2000, show_progress=True) as progress:
            assert progress.tracker is not None
            assert progress.rounds == 50
    
    def test_many_rounds_with_progress(self):
        """Test many rounds show progress."""
        with MillerRabinProgress(30, 500, show_progress=True) as progress:
            assert progress.tracker is not None
    
    def test_update(self):
        """Test progress updates."""
        with MillerRabinProgress(30, 2000, show_progress=True) as progress:
            if progress.tracker:
                progress.update(5)
                assert progress.tracker.current_iteration == 5


class TestBatchProgress:
    """Test batch progress tracker."""
    
    def test_init(self):
        """Test batch progress initialization."""
        with BatchProgress(100, "Testing") as progress:
            assert progress.total_numbers == 100
            assert progress.operation == "Testing"
            assert progress.results == {"prime": 0, "composite": 0, "error": 0}
    
    def test_update_results(self):
        """Test result updates."""
        with BatchProgress(10, "Testing") as progress:
            progress.update_result("prime")
            progress.update_result("composite")
            progress.update_result("prime")
            
            assert progress.results["prime"] == 2
            assert progress.results["composite"] == 1
            assert progress.results["error"] == 0
    
    def test_invalid_result(self):
        """Test handling of invalid result types."""
        with BatchProgress(10, "Testing") as progress:
            progress.update_result("invalid")
            # Should not crash, invalid results are ignored
            assert sum(progress.results.values()) == 0


class TestGenerationProgress:
    """Test generation progress tracker."""
    
    def test_random_mode_init(self):
        """Test random generation progress initialization."""
        with GenerationProgress(5, 64, "random") as progress:
            assert progress.target_count == 5
            assert progress.bits == 64
            assert progress.mode == "random"
            assert progress.found_count == 0
            assert progress.tested_count == 0
    
    def test_mersenne_mode_init(self):
        """Test Mersenne generation progress initialization."""
        with GenerationProgress(3, 128, "mersenne") as progress:
            assert progress.target_count == 3
            assert progress.mode == "mersenne"
    
    def test_update_tested(self):
        """Test updating tested candidates."""
        with GenerationProgress(5, 64, "random") as progress:
            progress.update_tested(is_prime=True)
            assert progress.found_count == 1
            assert progress.tested_count == 1
            
            progress.update_tested(is_prime=False)
            assert progress.found_count == 1
            assert progress.tested_count == 2
    
    def test_progress_calculation(self):
        """Test progress percentage calculation."""
        with GenerationProgress(4, 64, "random") as progress:
            progress.update_tested(is_prime=True)
            progress.update_tested(is_prime=True)
            
            # Should be 50% complete (2/4 found)
            assert progress.found_count == 2
            assert progress.target_count == 4


class TestProgressIntegration:
    """Integration tests for progress system."""
    
    @patch('prime_checker.progress.tqdm')
    def test_progress_with_mock_tqdm(self, mock_tqdm):
        """Test progress system with mocked tqdm."""
        mock_pbar = MagicMock()
        mock_tqdm.return_value = mock_pbar
        
        with ProgressTracker(100, "Test") as tracker:
            tracker.update(50)
            
        # Verify tqdm was called correctly
        mock_tqdm.assert_called_once()
        mock_pbar.update.assert_called()
        mock_pbar.close.assert_called_once()
    
    def test_no_progress_overhead(self):
        """Test that disabled progress has minimal overhead."""
        start_time = time.time()
        
        with LucasLehmerProgress(5, show_progress=False) as progress:
            for _ in range(1000):
                progress.update()
        
        elapsed = time.time() - start_time
        # Should be very fast (< 0.1 seconds) with no progress
        assert elapsed < 0.1