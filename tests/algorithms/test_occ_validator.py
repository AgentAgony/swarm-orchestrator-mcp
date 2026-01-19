"""
Tests for OCC Validator

Covers: version tracking, atomic writes, collision detection, retry logic
"""

import pytest
import tempfile
import os
from pathlib import Path

from mcp_core.algorithms.occ_validator import (
    OCCValidator, OCCResult, OCCStatus
)


class TestOCCValidator:
    """Test suite for OCC Validator"""
    
    @pytest.fixture
    def validator(self):
        """Create a fresh OCC validator"""
        return OCCValidator(max_retries=3, backoff_base=0.1)
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temporary file for testing"""
        file_path = tmp_path / "test_file.txt"
        file_path.write_text("initial content")
        return str(file_path)


class TestReadWithVersion(TestOCCValidator):
    """Tests for read_with_version method"""
    
    def test_read_existing_file(self, validator, temp_file):
        """Should read content and return SHA256 version"""
        content, version = validator.read_with_version(temp_file)
        
        assert content == "initial content"
        assert len(version) == 64  # SHA256 hex
    
    def test_read_nonexistent_file(self, validator, tmp_path):
        """Should return empty content and hash of empty string"""
        path = str(tmp_path / "nonexistent.txt")
        content, version = validator.read_with_version(path)
        
        assert content == ""
        assert len(version) == 64
    
    def test_version_changes_with_content(self, validator, temp_file):
        """Different content should produce different versions"""
        _, version1 = validator.read_with_version(temp_file)
        
        # Modify file
        with open(temp_file, "w") as f:
            f.write("modified content")
        
        _, version2 = validator.read_with_version(temp_file)
        
        assert version1 != version2


class TestValidateAndCommit(TestOCCValidator):
    """Tests for validate_and_commit method"""
    
    def test_successful_commit(self, validator, temp_file):
        """Should commit when version matches"""
        _, expected_version = validator.read_with_version(temp_file)
        
        result = validator.validate_and_commit(
            temp_file,
            new_content="new content",
            expected_version=expected_version
        )
        
        assert result.status == OCCStatus.SUCCESS
        assert result.new_version is not None
        
        # Verify file was actually updated
        with open(temp_file) as f:
            assert f.read() == "new content"
    
    def test_collision_on_version_mismatch(self, validator, temp_file):
        """Should detect collision when version doesn't match"""
        result = validator.validate_and_commit(
            temp_file,
            new_content="new content",
            expected_version="wrong_version",
            attempt_merge=False
        )
        
        assert result.status == OCCStatus.COLLISION
        assert "mismatch" in result.message.lower()
    
    def test_create_new_file(self, validator, tmp_path):
        """Should create file if it doesn't exist"""
        path = str(tmp_path / "new_file.txt")
        
        # Get version of nonexistent file
        _, version = validator.read_with_version(path)
        
        result = validator.validate_and_commit(
            path,
            new_content="brand new content",
            expected_version=version
        )
        
        assert result.status == OCCStatus.SUCCESS
        assert Path(path).exists()


class TestAtomicWrite(TestOCCValidator):
    """Tests for atomic write behavior"""
    
    def test_atomic_write_creates_file(self, validator, tmp_path):
        """Should create file atomically"""
        path = str(tmp_path / "atomic_test.txt")
        
        validator._atomic_write(path, "atomic content")
        
        assert Path(path).exists()
        with open(path) as f:
            assert f.read() == "atomic content"
    
    def test_atomic_write_creates_parent_dirs(self, validator, tmp_path):
        """Should create parent directories if needed"""
        path = str(tmp_path / "nested" / "dir" / "file.txt")
        
        validator._atomic_write(path, "nested content")
        
        assert Path(path).exists()


class TestComputeHash(TestOCCValidator):
    """Tests for hash computation"""
    
    def test_consistent_hash(self, validator):
        """Same content should produce same hash"""
        hash1 = validator._compute_hash("test content")
        hash2 = validator._compute_hash("test content")
        
        assert hash1 == hash2
    
    def test_different_content_different_hash(self, validator):
        """Different content should produce different hash"""
        hash1 = validator._compute_hash("content A")
        hash2 = validator._compute_hash("content B")
        
        assert hash1 != hash2
    
    def test_hash_is_sha256(self, validator):
        """Hash should be 64-character hex (SHA256)"""
        hash_val = validator._compute_hash("any content")
        
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)


class TestSemanticMerge(TestOCCValidator):
    """Tests for semantic merge attempts"""
    
    def test_identical_content_merge(self, validator):
        """Should succeed when content is identical"""
        result = validator.attempt_semantic_merge(
            base="same content",
            ours="same content",
            theirs="same content"
        )
        
        assert result == "same content"
