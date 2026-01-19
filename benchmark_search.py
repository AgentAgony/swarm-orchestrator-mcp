"""
Swarm Search Benchmark: Compare Swarm vs. Default Tools

This benchmark compares:
1. Swarm's Hybrid Search (semantic + keyword)
2. Standard grep-based search (simulating default tools)

Metrics measured:
- Indexing Time
- Search Latency
- Result Relevance (manual assessment via top-k results)
"""

import time
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any

from mcp_core.search_engine import (
    CodebaseIndexer,
    HybridSearch,
    IndexConfig,
    get_embedding_provider,
)


# ============================================================================
# Test Queries
# ============================================================================

TEST_QUERIES = [
    "authentication logic",
    "database models",
    "error handling",
    "user management",
    "search implementation",
]


# ============================================================================
# Swarm Search Benchmark
# ============================================================================

def benchmark_swarm_search(queries: List[str], use_embeddings: bool = False) -> Dict[str, Any]:
    """Benchmark Swarm's hybrid search."""
    print("=" * 60)
    print("SWARM HYBRID SEARCH BENCHMARK")
    print("=" * 60)
    
    # Initialize indexer
    config = IndexConfig(root_path=".", chunk_size=50, chunk_overlap=10)
    indexer = CodebaseIndexer(config)
    
    # Measure indexing time
    print("\n[1/3] Indexing codebase...")
    start_index = time.time()
    
    provider = None
    if use_embeddings:
        try:
            provider = get_embedding_provider("auto")
            print(f"✓ Using embedding provider: {type(provider).__name__}")
        except Exception as e:
            print(f"✗ Embeddings unavailable: {e}")
            print("  Falling back to keyword-only search")
    
    indexer.index_all(provider=provider)
    index_time = time.time() - start_index
    
    print(f"✓ Indexed {len(indexer.chunks)} chunks in {index_time:.2f}s")
    
    # Create searcher
    searcher = HybridSearch(indexer, provider=provider)
    
    # Measure search latency
    print("\n[2/3] Running search queries...")
    query_times = []
    results_summary = []
    
    for query in queries:
        start_search = time.time()
        
        if provider:
            results = searcher.search(query, top_k=3)
        else:
            results = searcher.keyword_search(query, top_k=3)
        
        search_time = time.time() - start_search
        query_times.append(search_time)
        
        print(f"\n  Query: '{query}'")
        print(f"  Time: {search_time*1000:.1f}ms | Results: {len(results)}")
        
        if results:
            top_result = results[0]
            file_name = Path(top_result.file_path).name
            print(f"  Top Result: {file_name}:{top_result.start_line} (score: {top_result.score:.3f})")
            
            results_summary.append({
                "query": query,
                "time_ms": search_time * 1000,
                "num_results": len(results),
                "top_file": file_name,
                "top_score": top_result.score,
            })
        else:
            print(f"  Top Result: None")
            results_summary.append({
                "query": query,
                "time_ms": search_time * 1000,
                "num_results": 0,
            })
    
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    
    print("\n[3/3] Summary")
    print(f"  Avg Query Time: {avg_query_time*1000:.1f}ms")
    
    return {
        "index_time": index_time,
        "avg_query_time_ms": avg_query_time * 1000,
        "total_chunks": len(indexer.chunks),
        "results": results_summary,
        "has_embeddings": provider is not None,
    }


# ============================================================================
# Default Tools Benchmark (grep-based)
# ============================================================================

def benchmark_default_tools(queries: List[str]) -> Dict[str, Any]:
    """Benchmark default grep-based search (simulating Antigravity tools)."""
    print("\n" + "=" * 60)
    print("DEFAULT TOOLS BENCHMARK (Python grep simulation)")
    print("=" * 60)
    
    # No indexing needed for grep
    index_time = 0
    
    print("\n[1/2] Running search queries with grep simulation...")
    query_times = []
    results_summary = []
    
    for query in queries:
        start_search = time.time()
        
        # Simple Python-based grep simulation
        match_files = []
        try:
            root = Path(".")
            for ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".md"]:
                for file_path in root.rglob(f"*{ext}"):
                    # Skip excluded directories
                    if any(excl in str(file_path) for excl in ["node_modules", "__pycache__", ".git", "dist", "build", ".venv"]):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if query.lower() in content.lower():
                            match_files.append(str(file_path))
                    except:
                        pass
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        search_time = time.time() - start_search
        query_times.append(search_time)
        
        print(f"\n  Query: '{query}'")
        print(f"  Time: {search_time*1000:.1f}ms | Files with matches: {len(match_files)}")
        
        if match_files:
            print(f"  Top Result: {Path(match_files[0]).name}")
            results_summary.append({
                "query": query,
                "time_ms": search_time * 1000,
                "num_files": len(match_files),
                "top_file": Path(match_files[0]).name,
            })
        else:
            print(f"  Top Result: None")
            results_summary.append({
                "query": query,
                "time_ms": search_time * 1000,
                "num_files": 0,
            })
    
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    
    print("\n[2/2] Summary")
    print(f"  Avg Query Time: {avg_query_time*1000:.1f}ms")
    
    return {
        "index_time": index_time,
        "avg_query_time_ms": avg_query_time * 1000,
        "results": results_summary,
    }


# ============================================================================
# Main Benchmark Runner
# ============================================================================

def main():
    """Run complete benchmark comparison."""
    print("\n" + "🔍 SWARM SEARCH BENCHMARK".center(60) + "\n")
    print("Comparing Swarm Hybrid Search vs. Default Tools (ripgrep)")
    print("=" * 60)
    
    # Check if embeddings are available
    has_api_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    
    if has_api_key:
        print("✓ API key detected - running semantic search comparison")
        swarm_results = benchmark_swarm_search(TEST_QUERIES, use_embeddings=True)
    else:
        print("⚠ No API key - running keyword-only comparison")
        swarm_results = benchmark_swarm_search(TEST_QUERIES, use_embeddings=False)
    
    default_results = benchmark_default_tools(TEST_QUERIES)
    
    # Print comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    print(f"\nIndexing Time:")
    print(f"  Swarm: {swarm_results['index_time']:.2f}s")
    print(f"  Default: {default_results['index_time']:.2f}s (no indexing required)")
    
    print(f"\nAverage Query Time:")
    print(f"  Swarm: {swarm_results['avg_query_time_ms']:.1f}ms")
    print(f"  Default: {default_results['avg_query_time_ms']:.1f}ms")
    
    speedup = default_results['avg_query_time_ms'] / swarm_results['avg_query_time_ms'] if swarm_results['avg_query_time_ms'] > 0 else 0
    
    if speedup > 1:
        print(f"  → Swarm is {speedup:.1f}x faster")
    else:
        print(f"  → Default is {1/speedup:.1f}x faster")
    
    print(f"\nSwarm Chunks: {swarm_results['total_chunks']}")
    print(f"Semantic Search: {'Enabled' if swarm_results['has_embeddings'] else 'Disabled (keyword-only)'}")
    
    # Return results for potential parsing
    return {
        "swarm": swarm_results,
        "default": default_results,
    }


if __name__ == "__main__":
    main()
