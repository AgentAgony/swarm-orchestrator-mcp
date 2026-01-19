"""
Tests for HippoRAG Retriever

Covers: AST graph building, PPR retrieval, seed node detection
"""

import pytest
import tempfile
from pathlib import Path

# Skip tests if networkx not available
pytest.importorskip("networkx")

from mcp_core.algorithms.hipporag_retriever import (
    HippoRAGRetriever, ContextChunk
)


class TestHippoRAGRetriever:
    """Test suite for HippoRAG Retriever"""
    
    @pytest.fixture
    def retriever(self):
        """Create a fresh retriever"""
        return HippoRAGRetriever()
    
    @pytest.fixture
    def sample_codebase(self, tmp_path):
        """Create a sample Python codebase for testing"""
        # Create a simple Python file
        code1 = '''
def helper_function():
    """A helper function"""
    return 42

def main_function():
    """Calls the helper"""
    result = helper_function()
    return result * 2

class Calculator:
    """A simple calculator"""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
        
        code2 = '''
from typing import List

class DataProcessor:
    """Processes data"""
    
    def process(self, data: List[int]) -> int:
        return sum(data)
'''
        
        (tmp_path / "module1.py").write_text(code1)
        (tmp_path / "module2.py").write_text(code2)
        
        return str(tmp_path)


class TestBuildGraph(TestHippoRAGRetriever):
    """Tests for AST graph building"""
    
    def test_build_graph_from_ast(self, retriever, sample_codebase):
        """Should build graph from Python files"""
        graph = retriever.build_graph_from_ast(sample_codebase)
        
        assert graph is not None
        assert graph.number_of_nodes() > 0
        assert graph.number_of_edges() >= 0
    
    def test_graph_contains_functions(self, retriever, sample_codebase):
        """Graph should contain function nodes"""
        retriever.build_graph_from_ast(sample_codebase)
        
        # Check that functions are in metadata
        node_names = [m["node_name"] for m in retriever.node_metadata.values()]
        
        assert "helper_function" in node_names
        assert "main_function" in node_names
    
    def test_graph_contains_classes(self, retriever, sample_codebase):
        """Graph should contain class nodes"""
        retriever.build_graph_from_ast(sample_codebase)
        
        node_names = [m["node_name"] for m in retriever.node_metadata.values()]
        
        assert "Calculator" in node_names
        assert "DataProcessor" in node_names
    
    def test_empty_directory(self, retriever, tmp_path):
        """Should handle empty directory gracefully"""
        graph = retriever.build_graph_from_ast(str(tmp_path))
        
        assert graph.number_of_nodes() == 0


class TestRetrieveContext(TestHippoRAGRetriever):
    """Tests for PPR-based context retrieval"""
    
    def test_retrieve_matching_query(self, retriever, sample_codebase):
        """Should retrieve chunks matching query"""
        retriever.build_graph_from_ast(sample_codebase)
        
        chunks = retriever.retrieve_context("Calculator", top_k=5)
        
        assert len(chunks) > 0
        assert any("Calculator" in c.node_name for c in chunks)
    
    def test_retrieve_returns_context_chunks(self, retriever, sample_codebase):
        """Results should be ContextChunk objects"""
        retriever.build_graph_from_ast(sample_codebase)
        
        chunks = retriever.retrieve_context("function", top_k=3)
        
        for chunk in chunks:
            assert isinstance(chunk, ContextChunk)
            assert chunk.file_path
            assert chunk.node_name
            assert chunk.ppr_score >= 0
    
    def test_retrieve_no_match(self, retriever, sample_codebase):
        """Should return empty for non-matching query"""
        retriever.build_graph_from_ast(sample_codebase)
        
        chunks = retriever.retrieve_context("zzz_nonexistent_zzz", top_k=5)
        
        assert chunks == []
    
    def test_retrieve_requires_graph(self, retriever):
        """Should raise if graph not built"""
        with pytest.raises(ValueError):
            retriever.retrieve_context("anything")
    
    def test_top_k_limits_results(self, retriever, sample_codebase):
        """Should respect top_k parameter"""
        retriever.build_graph_from_ast(sample_codebase)
        
        chunks = retriever.retrieve_context("function", top_k=2)
        
        assert len(chunks) <= 2


class TestSeedNodeDetection(TestHippoRAGRetriever):
    """Tests for seed node finding"""
    
    def test_find_seed_nodes(self, retriever, sample_codebase):
        """Should find nodes matching query"""
        retriever.build_graph_from_ast(sample_codebase)
        
        seeds = retriever._find_seed_nodes("helper")
        
        assert len(seeds) > 0
        assert any("helper" in s.lower() for s in seeds)
    
    def test_case_insensitive_search(self, retriever, sample_codebase):
        """Should match regardless of case"""
        retriever.build_graph_from_ast(sample_codebase)
        
        seeds_lower = retriever._find_seed_nodes("calculator")
        seeds_upper = retriever._find_seed_nodes("CALCULATOR")
        
        assert len(seeds_lower) > 0
        assert len(seeds_upper) > 0


class TestMetadata(TestHippoRAGRetriever):
    """Tests for node metadata storage"""
    
    def test_metadata_stored(self, retriever, sample_codebase):
        """Should store metadata for each node"""
        retriever.build_graph_from_ast(sample_codebase)
        
        assert len(retriever.node_metadata) > 0
        
        for node_id, meta in retriever.node_metadata.items():
            assert "file_path" in meta
            assert "node_name" in meta
            assert "node_type" in meta
            assert "start_line" in meta
            assert "content" in meta
