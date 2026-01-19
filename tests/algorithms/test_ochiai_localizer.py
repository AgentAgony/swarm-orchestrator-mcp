"""
Tests for Ochiai Localizer (SBFL)

Covers: suspiciousness calculation, debug prompt generation
Note: Coverage collection tests are limited due to subprocess complexity
"""

import pytest
import math

# Skip if coverage not available
coverage = pytest.importorskip("coverage")

from mcp_core.algorithms.ochiai_localizer import (
    OchiaiLocalizer, CoverageSpectrum
)


class TestOchiaiLocalizer:
    """Test suite for Ochiai Localizer"""
    
    @pytest.fixture
    def localizer(self):
        """Create a fresh Ochiai localizer"""
        return OchiaiLocalizer()


class TestSuspiciousnessCalculation(TestOchiaiLocalizer):
    """Tests for Ochiai suspiciousness formula"""
    
    def test_calculate_pure_failing(self, localizer):
        """Line only in failing tests should have high suspicion"""
        spectrum = CoverageSpectrum(
            passed_tests={"file.py": set()},
            failed_tests={"file.py": {10}},  # Line 10 only in failing
            total_passed=1,
            total_failed=1
        )
        
        suspiciousness = localizer.calculate_suspiciousness(spectrum)
        
        assert ("file.py", 10) in suspiciousness
        assert suspiciousness[("file.py", 10)] == 1.0  # Max suspicion
    
    def test_calculate_pure_passing(self, localizer):
        """Line only in passing tests should have zero suspicion"""
        spectrum = CoverageSpectrum(
            passed_tests={"file.py": {10}},  # Line 10 only in passing
            failed_tests={"file.py": set()},
            total_passed=1,
            total_failed=1
        )
        
        suspiciousness = localizer.calculate_suspiciousness(spectrum)
        
        assert ("file.py", 10) in suspiciousness
        assert suspiciousness[("file.py", 10)] == 0.0  # Zero suspicion
    
    def test_calculate_mixed_coverage(self, localizer):
        """Line in both should have partial suspicion"""
        spectrum = CoverageSpectrum(
            passed_tests={"file.py": {10}},
            failed_tests={"file.py": {10}},
            total_passed=1,
            total_failed=1
        )
        
        suspiciousness = localizer.calculate_suspiciousness(spectrum)
        
        score = suspiciousness[("file.py", 10)]
        assert 0 < score < 1  # Partial suspicion
    
    def test_ochiai_formula(self, localizer):
        """Should use correct Ochiai formula"""
        # Ochiai: failed(l) / sqrt(total_failed * (failed(l) + passed(l)))
        spectrum = CoverageSpectrum(
            passed_tests={"file.py": {10}},
            failed_tests={"file.py": {10}},
            total_passed=3,
            total_failed=1
        )
        
        suspiciousness = localizer.calculate_suspiciousness(spectrum)
        
        # failed(10) = 1, passed(10) = 1, total_failed = 1
        # expected = 1 / sqrt(1 * (1 + 1)) = 1 / sqrt(2) ≈ 0.707
        expected = 1.0 / math.sqrt(1 * 2)
        assert suspiciousness[("file.py", 10)] == pytest.approx(expected)


class TestTopSuspiciousLines(TestOchiaiLocalizer):
    """Tests for ranked line retrieval"""
    
    def test_get_top_k(self, localizer):
        """Should return top k most suspicious lines"""
        suspiciousness = {
            ("file.py", 10): 0.9,
            ("file.py", 20): 0.5,
            ("file.py", 30): 0.8,
            ("file.py", 40): 0.3,
        }
        
        top = localizer.get_top_suspicious_lines(suspiciousness, top_k=2)
        
        assert len(top) == 2
        assert top[0] == ("file.py", 10, 0.9)  # Highest first
        assert top[1] == ("file.py", 30, 0.8)
    
    def test_sorted_by_score(self, localizer):
        """Results should be sorted by descending score"""
        suspiciousness = {
            ("a.py", 1): 0.1,
            ("b.py", 2): 0.9,
            ("c.py", 3): 0.5,
        }
        
        top = localizer.get_top_suspicious_lines(suspiciousness, top_k=3)
        
        scores = [t[2] for t in top]
        assert scores == sorted(scores, reverse=True)


class TestDebugPromptGeneration(TestOchiaiLocalizer):
    """Tests for debug prompt creation"""
    
    def test_generate_prompt(self, localizer):
        """Should generate formatted debug prompt"""
        suspicious = [
            ("file.py", 10, 0.9),
            ("file.py", 20, 0.7),
        ]
        
        prompt = localizer.generate_debug_prompt(suspicious)
        
        assert "file.py" in prompt
        assert "L10" in prompt
        assert "0.9" in prompt or "0.90" in prompt
    
    def test_empty_suspicious_lines(self, localizer):
        """Should handle empty suspicious list"""
        prompt = localizer.generate_debug_prompt([])
        
        assert "No suspicious lines" in prompt
    
    def test_includes_action_required(self, localizer):
        """Prompt should include action guidance"""
        suspicious = [("file.py", 10, 0.9)]
        
        prompt = localizer.generate_debug_prompt(suspicious)
        
        assert "Action Required" in prompt or "action" in prompt.lower()


class TestCoverageSpectrum:
    """Tests for CoverageSpectrum data structure"""
    
    def test_spectrum_structure(self):
        """Spectrum should have correct fields"""
        spectrum = CoverageSpectrum(
            passed_tests={"file.py": {1, 2, 3}},
            failed_tests={"file.py": {2, 3, 4}},
            total_passed=5,
            total_failed=2
        )
        
        assert spectrum.total_passed == 5
        assert spectrum.total_failed == 2
        assert 1 in spectrum.passed_tests["file.py"]
        assert 4 in spectrum.failed_tests["file.py"]
