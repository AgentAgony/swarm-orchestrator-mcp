"""
HippoRAG Retriever - Knowledge Graph Retrieval with Personalized PageRank

Implements GraphRAG from v3.0 spec Section 5.3.
Builds knowledge graphs from AST and uses PPR for deep context retrieval.
"""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    import networkx as nx

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None  # type: ignore
    logging.warning(
        "networkx not installed. GraphRAG functionality disabled. "
        "Install with: pip install networkx>=3.0"
    )

logger = logging.getLogger(__name__)


@dataclass
class ContextChunk:
    """A piece of code context retrieved via PPR"""
    file_path: str
    node_name: str
    node_type: str  # function, class, method, etc.
    content: str
    ppr_score: float
    start_line: int
    end_line: int


class HippoRAGRetriever:
    """
    Knowledge graph retrieval using Personalized PageRank.
    
    Mimics human associative memory by traversing structural relationships
    in code (calls, imports, inheritance) to find relevant context.
    """
    
    def __init__(self):
        """Initialize retriever with empty graph"""
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "networkx is required for HippoRAG. "
                "Install with: pip install networkx>=3.0"
            )
        
        self.graph: Optional['nx.DiGraph'] = None
        self.node_metadata: Dict[str, Dict] = {}
    
    def build_graph_from_ast(
        self,
        codebase_path: str,
        extensions: List[str] = [".py"]
    ) -> 'nx.DiGraph':
        """
        Extract function calls, imports, and class inheritance from AST.
        
        Args:
            codebase_path: Root directory of codebase
            extensions: File extensions to analyze
            
        Returns:
            Directed graph with code entities as nodes
        """
        graph = nx.DiGraph()
        base_path = Path(codebase_path)
        
        # Scan Python files
        py_files = []
        for ext in extensions:
            py_files.extend(base_path.rglob(f"*{ext}"))
        
        logger.info(f"Building AST graph from {len(py_files)} files")
        
        for file_path in py_files:
            try:
                self._process_file(graph, file_path)
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
                continue
        
        self.graph = graph
        logger.info(
            f"Graph built: {graph.number_of_nodes()} nodes, "
            f"{graph.number_of_edges()} edges"
        )
        
        return graph
    
    def _process_file(self, graph: 'nx.DiGraph', file_path: Path) -> None:
        """
        Parse a single file and add nodes/edges to graph.
        
        Args:
            graph: NetworkX graph to populate
            file_path: Path to Python file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return
        
        rel_path = str(file_path)
        
        # Extract top-level entities
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._add_function_node(graph, node, rel_path, source)
            elif isinstance(node, ast.ClassDef):
                self._add_class_node(graph, node, rel_path, source)
    
    def _add_function_node(
        self,
        graph: 'nx.DiGraph',
        node: ast.FunctionDef,
        file_path: str,
        source: str
    ) -> None:
        """Add function node and extract call edges"""
        func_name = f"{file_path}::{node.name}"
        
        # Add node
        graph.add_node(
            func_name,
            type="function",
            file=file_path,
            line=node.lineno
        )
        
        # Store metadata for retrieval
        self.node_metadata[func_name] = {
            "file_path": file_path,
            "node_name": node.name,
            "node_type": "function",
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
            "content": self._extract_source(source, node)
        }
        
        # Extract function calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    called_name = child.func.id
                    # Add edge: this function calls another
                    target = f"{file_path}::{called_name}"
                    graph.add_edge(func_name, target, type="calls")
    
    def _add_class_node(
        self,
        graph: 'nx.DiGraph',
        node: ast.ClassDef,
        file_path: str,
        source: str
    ) -> None:
        """Add class node and extract inheritance edges"""
        class_name = f"{file_path}::{node.name}"
        
        # Add node
        graph.add_node(
            class_name,
            type="class",
            file=file_path,
            line=node.lineno
        )
        
        self.node_metadata[class_name] = {
            "file_path": file_path,
            "node_name": node.name,
            "node_type": "class",
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
            "content": self._extract_source(source, node)
        }
        
        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                parent_name = f"{file_path}::{base.id}"
                graph.add_edge(class_name, parent_name, type="inherits")
    
    def _extract_source(self, source: str, node: ast.AST) -> str:
        """Extract source code for AST node"""
        lines = source.splitlines()
        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        
        return "\n".join(lines[start:end])
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.85
    ) -> List[ContextChunk]:
        """
        Retrieve relevant code using Personalized PageRank.
        
        Args:
            query: Search query (function/class name or description)
            top_k: Number of results to return
            alpha: PPR damping factor (0-1)
            
        Returns:
            List of ContextChunks ranked by PPR score
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build_graph_from_ast() first")
        
        # Find seed nodes matching query
        seed_nodes = self._find_seed_nodes(query)
        
        if not seed_nodes:
            logger.warning(f"No seed nodes found for query: {query}")
            return []
        
        # Run Personalized PageRank from seeds
        personalization = {node: 1.0 / len(seed_nodes) for node in seed_nodes}
        
        try:
            ppr_scores = nx.pagerank(
                self.graph,
                alpha=alpha,
                personalization=personalization,
                max_iter=100
            )
        except Exception as e:
            logger.error(f"PageRank failed: {e}")
            return []
        
        # Sort nodes by PPR score
        ranked_nodes = sorted(
            ppr_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Convert to ContextChunks
        results = []
        for node_id, score in ranked_nodes:
            if node_id in self.node_metadata:
                meta = self.node_metadata[node_id]
                results.append(ContextChunk(
                    file_path=meta["file_path"],
                    node_name=meta["node_name"],
                    node_type=meta["node_type"],
                    content=meta["content"],
                    ppr_score=score,
                    start_line=meta["start_line"],
                    end_line=meta["end_line"]
                ))
        
        logger.info(f"Retrieved {len(results)} context chunks for: {query}")
        return results
    
    def _find_seed_nodes(self, query: str) -> List[str]:
        """
        Find graph nodes matching the query.
        
        Simple substring matching on node names.
        Production version would use embeddings.
        
        Args:
            query: Search string
            
        Returns:
            List of matching node IDs
        """
        query_lower = query.lower()
        seeds = []
        
        for node_id in self.graph.nodes():
            # Extract function/class name from ID
            if "::" in node_id:
                name = node_id.split("::")[-1]
                if query_lower in name.lower():
                    seeds.append(node_id)
        
        return seeds
    
    def add_semantic_edges(
        self,
        entities: Dict[str, List[str]]
    ) -> None:
        """
        Add edges from NLP entity extraction.
        
        Args:
            entities: Dict mapping entity names to related entities
        """
        if self.graph is None:
            raise ValueError("Graph not built")
        
        for source, targets in entities.items():
            for target in targets:
                if source in self.graph and target in self.graph:
                    self.graph.add_edge(source, target, type="related_to")
        
        logger.info(f"Added {len(entities)} semantic edges")
