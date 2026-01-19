"""
Swarm v3.0 - FastMCP Server

Exposes the Swarm orchestrator functionality as an MCP server.
This allows AI agents (like Claude Desktop, VSCode, etc.) to interact
with the Swarm via the Model Context Protocol.
"""

import logging
from typing import Optional
from fastmcp import FastMCP

# Import Swarm components
from mcp_core.orchestrator_loop import Orchestrator
from mcp_core.swarm_schemas import Task
from mcp_core.search_engine import CodebaseIndexer, HybridSearch, IndexConfig, get_embedding_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Swarm Orchestrator v3.0")

# Initialize orchestrator (lazy)
_orchestrator: Optional[Orchestrator] = None
_indexer: Optional[CodebaseIndexer] = None


def get_orchestrator() -> Orchestrator:
    """Lazy-load orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        logger.info("🚀 Initializing Swarm Orchestrator...")
        _orchestrator = Orchestrator()
    return _orchestrator


def get_indexer() -> CodebaseIndexer:
    """Lazy-load indexer instance."""
    global _indexer
    if _indexer is None:
        logger.info("📚 Initializing Codebase Indexer...")
        config = IndexConfig()
        _indexer = CodebaseIndexer(config)
        _indexer.load_cache()  # Try to load existing index
    return _indexer


@mcp.tool()
def process_task(instruction: str) -> str:
    """
    Create and process a task in the Swarm orchestrator.
    
    Args:
        instruction: The task instruction/description
        
    Returns:
        Task ID and initial status
    """
    try:
        orch = get_orchestrator()
        
        # Create a new task
        task = Task(description=instruction)
        task_id = task.task_id
        
        # Add to orchestrator state
        orch.state.tasks[task_id] = task
        orch.save_state()
        
        # Process the task
        orch.process_task(task_id)
        
        # Reload to get updated status
        orch.load_state()
        updated_task = orch.state.tasks[task_id]
        
        return f"✅ Task {task_id[:8]} created and processed.\nStatus: {updated_task.status}\nFeedback: {updated_task.feedback_log[-1] if updated_task.feedback_log else 'None'}"
        
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def get_status() -> str:
    """
    Get the current status of all tasks in the Swarm blackboard.
    
    Returns:
        Formatted status of all tasks
    """
    try:
        orch = get_orchestrator()
        orch.load_state()
        
        if not orch.state.tasks:
            return "📋 No tasks found in the blackboard."
        
        status_lines = ["📋 Swarm Blackboard Status:\n"]
        for task_id, task in orch.state.tasks.items():
            status_lines.append(f"  • {task_id[:8]}: [{task.status}] {task.description[:50]}...")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def search_codebase(query: str, top_k: int = 5, keyword_only: bool = False) -> str:
    """
    Search the codebase using hybrid semantic + keyword search.
    
    Args:
        query: Search query (natural language or keywords)
        top_k: Number of results to return (default 5)
        keyword_only: Use only keyword matching (default False)
        
    Returns:
        Formatted search results with file paths and snippets
    """
    try:
        indexer = get_indexer()
        
        if not indexer.chunks:
            return "⚠️ No index found. Please run 'index' command first."
        
        # Get embedding provider for hybrid search (optional)
        embed_provider = None
        if not keyword_only:
            has_embeddings = any(c.embedding is not None for c in indexer.chunks)
            if has_embeddings:
                try:
                    embed_provider = get_embedding_provider("auto")
                except RuntimeError:
                    logger.warning("No API key set, falling back to keyword search")
        
        # Perform search
        searcher = HybridSearch(indexer, embed_provider)
        
        if keyword_only:
            results = searcher.keyword_search(query, top_k=top_k)
        else:
            results = searcher.search(query, top_k=top_k)
        
        if not results:
            return "🔍 No results found."
        
        # Format results
        result_lines = [f"🔍 Found {len(results)} results for: {query}\n"]
        for i, result in enumerate(results, 1):
            result_lines.append(f"{i}. {result.file_path}:{result.start_line}-{result.end_line}")
            result_lines.append(f"   Score: {result.score:.3f}")
            result_lines.append(f"   {result.content[:200]}...\n")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        logger.error(f"Error searching codebase: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def index_codebase(path: str = ".", provider: str = "auto") -> str:
    """
    Index the codebase for semantic search.
    
    Args:
        path: Path to codebase (default current directory)
        provider: Embedding provider (gemini, openai, local, auto)
        
    Returns:
        Indexing status and statistics
    """
    try:
        config = IndexConfig(root_path=path)
        indexer = CodebaseIndexer(config)
        
        # Try to get embedding provider
        try:
            embed_provider = get_embedding_provider(provider)
            logger.info(f"Using embedding provider: {type(embed_provider).__name__}")
            indexer.index_all(embed_provider)
        except RuntimeError as e:
            logger.warning(f"⚠️ {e}")
            logger.warning("Indexing files without embeddings (keyword search only)")
            indexer.index_all(None)
        
        # Update global indexer
        global _indexer
        _indexer = indexer
        
        return f"✅ Indexed {len(indexer.chunks)} chunks from {path}"
        
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def retrieve_context(query: str, top_k: int = 10) -> str:
    """
    Use HippoRAG to retrieve relevant code context via AST graph + PageRank.
    More powerful than keyword search for finding related functionality.
    
    Args:
        query: Query to retrieve context for
        top_k: Number of context chunks to return (default 10)
        
    Returns:
        Formatted context chunks with relevance scores
    """
    try:
        from mcp_core.algorithms import HippoRAGRetriever
        
        retriever = HippoRAGRetriever()
        
        logger.info("📊 Building AST knowledge graph...")
        retriever.build_graph_from_ast(".", extensions=[".py"])
        
        logger.info(f"🔗 Graph: {retriever.graph.number_of_nodes()} nodes, {retriever.graph.number_of_edges()} edges")
        
        chunks = retriever.retrieve_context(query, top_k=top_k)
        
        if not chunks:
            return "🔍 No context found."
        
        result_lines = [f"🔍 Retrieved {len(chunks)} context chunks for: {query}\n"]
        for i, chunk in enumerate(chunks, 1):
            result_lines.append(f"{i}. [{chunk.node_type}] {chunk.node_name}")
            result_lines.append(f"   {chunk.file_path}:{chunk.start_line}-{chunk.end_line}")
            result_lines.append(f"   PPR Score: {chunk.ppr_score:.4f}")
            result_lines.append(f"   {chunk.content[:150]}...\n")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return f"❌ Error: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    logger.info("🚀 Starting Swarm MCP Server...")
    mcp.run()
