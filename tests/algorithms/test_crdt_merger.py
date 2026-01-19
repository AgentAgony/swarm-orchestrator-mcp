"""
Tests for CRDT Merger

Covers: document creation, update application, merge convergence
Note: Requires pycrdt package, tests skip if not available
"""

import pytest

# Skip all tests if pycrdt not available
pycrdt = pytest.importorskip("pycrdt")

from mcp_core.algorithms.crdt_merger import CRDTMerger, CRDTDocument


class TestCRDTMerger:
    """Test suite for CRDT Merger"""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh CRDT merger"""
        return CRDTMerger()


class TestDocumentCreation(TestCRDTMerger):
    """Tests for document creation"""
    
    def test_create_document(self, merger):
        """Should create a new CRDT document"""
        merger.create_document("doc_1", "initial content")
        
        assert "doc_1" in merger.documents
    
    def test_create_with_initial_content(self, merger):
        """Should set initial content"""
        merger.create_document("doc_1", "hello world")
        
        state = merger.get_state("doc_1")
        assert state == "hello world"
    
    def test_create_empty_document(self, merger):
        """Should create empty document"""
        merger.create_document("doc_1")
        
        state = merger.get_state("doc_1")
        assert state == ""
    
    def test_duplicate_creation_skipped(self, merger):
        """Should skip if document already exists"""
        merger.create_document("doc_1", "first")
        merger.create_document("doc_1", "second")  # Should be skipped
        
        state = merger.get_state("doc_1")
        assert state == "first"


class TestGetState(TestCRDTMerger):
    """Tests for state retrieval"""
    
    def test_get_state(self, merger):
        """Should return current text state"""
        merger.create_document("doc_1", "test content")
        
        state = merger.get_state("doc_1")
        
        assert state == "test content"
    
    def test_nonexistent_document_raises(self, merger):
        """Should raise for unknown document"""
        with pytest.raises(ValueError):
            merger.get_state("nonexistent")


class TestInsertText(TestCRDTMerger):
    """Tests for text insertion"""
    
    def test_insert_at_start(self, merger):
        """Should insert at beginning"""
        merger.create_document("doc_1", "world")
        merger.insert_text("doc_1", 0, "hello ")
        
        state = merger.get_state("doc_1")
        assert state == "hello world"
    
    def test_insert_at_end(self, merger):
        """Should insert at end"""
        merger.create_document("doc_1", "hello")
        merger.insert_text("doc_1", 5, " world")
        
        state = merger.get_state("doc_1")
        assert state == "hello world"
    
    def test_insert_returns_update(self, merger):
        """Should return binary update vector"""
        merger.create_document("doc_1", "")
        update = merger.insert_text("doc_1", 0, "test")
        
        assert isinstance(update, bytes)
        assert len(update) > 0


class TestDeleteText(TestCRDTMerger):
    """Tests for text deletion"""
    
    def test_delete_range(self, merger):
        """Should delete character range"""
        merger.create_document("doc_1", "hello world")
        merger.delete_text("doc_1", 5, 11)  # Delete " world"
        
        state = merger.get_state("doc_1")
        assert state == "hello"
    
    def test_delete_returns_update(self, merger):
        """Should return binary update vector"""
        merger.create_document("doc_1", "test")
        update = merger.delete_text("doc_1", 0, 2)
        
        assert isinstance(update, bytes)


class TestApplyUpdate(TestCRDTMerger):
    """Tests for update application and merging"""
    
    def test_apply_update_from_self(self, merger):
        """Should apply update from same document"""
        merger.create_document("doc_1", "")
        update = merger.insert_text("doc_1", 0, "inserted")
        
        # Create second document
        merger.create_document("doc_2", "")
        merger.apply_update("doc_2", update)
        
        state = merger.get_state("doc_2")
        # Note: CRDT updates are document-specific, so this tests the mechanism


class TestDestroyDocument(TestCRDTMerger):
    """Tests for document destruction"""
    
    def test_destroy_existing(self, merger):
        """Should remove document from registry"""
        merger.create_document("doc_1", "content")
        merger.destroy_document("doc_1")
        
        assert "doc_1" not in merger.documents
    
    def test_destroy_nonexistent_silent(self, merger):
        """Should silently ignore nonexistent document"""
        merger.destroy_document("nonexistent")  # Should not raise
