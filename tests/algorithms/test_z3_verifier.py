"""
Tests for Z3 Verifier

Covers: symbolic verification, counterexample generation
Note: Requires z3-solver package, tests skip if not available
"""

import pytest

# Skip all tests if z3 not available
z3 = pytest.importorskip("z3")

from mcp_core.algorithms.z3_verifier import (
    Z3Verifier, VerificationResult, create_symbolic_int, create_symbolic_bool
)


class TestZ3Verifier:
    """Test suite for Z3 Verifier"""
    
    @pytest.fixture
    def verifier(self):
        """Create a fresh Z3 verifier"""
        return Z3Verifier(timeout_ms=5000)


class TestSymbolicVariables:
    """Tests for symbolic variable creation"""
    
    def test_create_symbolic_int(self):
        """Should create symbolic integer"""
        x = create_symbolic_int("x")
        
        assert x is not None
        assert str(x) == "x"
    
    def test_create_symbolic_bool(self):
        """Should create symbolic boolean"""
        b = create_symbolic_bool("flag")
        
        assert b is not None
        assert str(b) == "flag"


class TestVerifyFunction(TestZ3Verifier):
    """Tests for function verification"""
    
    def test_verify_tautology(self, verifier):
        """Should verify always-true postcondition"""
        x = z3.Int("x")
        
        # Postcondition: x == x (always true)
        result = verifier.verify_function(
            func=None,
            preconditions=[],
            postconditions=[x == x]
        )
        
        assert result.verified
    
    def test_verify_with_precondition(self, verifier):
        """Should verify with precondition"""
        x = z3.Int("x")
        
        # Precondition: x > 0
        # Postcondition: x + 1 > 0 (true when x > 0)
        result = verifier.verify_function(
            func=None,
            preconditions=[x > 0],
            postconditions=[x + 1 > 0]
        )
        
        assert result.verified
    
    def test_detect_violation(self, verifier):
        """Should detect postcondition violation"""
        x = z3.Int("x")
        
        # Postcondition: x > 100 (not always true)
        result = verifier.verify_function(
            func=None,
            preconditions=[],
            postconditions=[x > 100]
        )
        
        assert not result.verified
        assert result.counterexample is not None
    
    def test_counterexample_values(self, verifier):
        """Counterexample should contain violating values"""
        x = z3.Int("x")
        
        # Should find x <= 0 as counterexample
        result = verifier.verify_function(
            func=None,
            preconditions=[],
            postconditions=[x > 0]
        )
        
        assert not result.verified
        assert "x" in result.counterexample
        assert result.counterexample["x"] <= 0


class TestFindCounterexample(TestZ3Verifier):
    """Tests for counterexample finding"""
    
    def test_find_counterexample(self, verifier):
        """Should find violating input"""
        x = z3.Int("x")
        
        # Find x where x > 0 is false (i.e., x <= 0)
        counter = verifier.find_counterexample(x > 0)
        
        assert counter is not None
        assert counter["x"] <= 0
    
    def test_no_counterexample_for_tautology(self, verifier):
        """Should return None for tautology"""
        x = z3.Int("x")
        
        # x == x is always true, no counterexample
        counter = verifier.find_counterexample(x == x)
        
        assert counter is None


class TestVerificationResult:
    """Tests for verification result structure"""
    
    def test_result_structure(self):
        """Result should have correct fields"""
        result = VerificationResult(
            verified=True,
            message="Success"
        )
        
        assert result.verified
        assert result.message == "Success"
        assert result.counterexample is None
    
    def test_result_with_counterexample(self):
        """Result should store counterexample"""
        result = VerificationResult(
            verified=False,
            message="Failed",
            counterexample={"x": -5}
        )
        
        assert not result.verified
        assert result.counterexample["x"] == -5
