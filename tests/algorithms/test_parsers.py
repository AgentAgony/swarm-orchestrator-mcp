"""
Tests for multi-language parser infrastructure.

Tests the parser registry, Python parser, and optional JavaScript/TypeScript parsers.
"""

import pytest
from mcp_core.algorithms.parsers import (
    ParserRegistry,
    PythonParser,
    ASTNode
)


def _treesitter_available() -> bool:
    """Check if Tree-sitter packages are installed"""
    try:
        import tree_sitter
        import tree_sitter_javascript
        import tree_sitter_typescript
        return True
    except ImportError:
        return False


class TestParserRegistry:
    """Test parser registry functionality"""
    
    def test_registry_initialized_with_python(self):
        """Python parser should always be registered"""
        registry = ParserRegistry()
        assert "Python" in registry.supported_languages()
        assert ".py" in registry.supported_extensions()
    
    def test_get_parser_for_python_file(self):
        """Should return Python parser for .py files"""
        registry = ParserRegistry()
        parser = registry.get_parser_for_file("test.py")
        assert parser is not None
        assert parser.language_name == "Python"
    
    def test_unknown_extension_returns_none(self):
        """Should return None for unsupported extensions"""
        registry = ParserRegistry()
        parser = registry.get_parser_for_file("test.unknown")
        assert parser is None


class TestPythonParser:
    """Test Python AST parser"""
    
    def test_extensions(self):
        """Should handle .py and .pyw files"""
        parser = PythonParser()
        assert ".py" in parser.extensions
        assert ".pyw" in parser.extensions
    
    def test_language_name(self):
        """Should identify as Python"""
        parser = PythonParser()
        assert parser.language_name == "Python"
    
    def test_parse_simple_function(self):
        """Should parse simple function definition"""
        parser = PythonParser()
        source = '''
def hello(name):
    print(f"Hello, {name}")
    return None
'''
        nodes = parser.parse_file("test.py", source)
        
        assert len(nodes) == 1
        assert nodes[0].name == "hello"
        assert nodes[0].node_type == "function"
        assert nodes[0].file_path == "test.py"
        assert "print" in nodes[0].calls
    
    def test_parse_class(self):
        """Should parse class definition with inheritance"""
        parser = PythonParser()
        source = '''
class Dog(Animal):
    def bark(self):
        print("Woof!")
'''
        nodes = parser.parse_file("test.py", source)
        
        # Should find both class and method
        class_node = next(n for n in nodes if n.node_type == "class")
        assert class_node.name == "Dog"
        assert "Animal" in class_node.inherits
    
    def test_parse_function_calls(self):
        """Should extract function calls"""
        parser = PythonParser()
        source = '''
def process():
    setup()
    validate()
    teardown()
'''
        nodes = parser.parse_file("test.py", source)
        
        assert len(nodes) == 1
        calls = nodes[0].calls
        assert "setup" in calls
        assert "validate" in calls
        assert "teardown" in calls
    
    def test_syntax_error_raises(self):
        """Should raise SyntaxError for invalid Python"""
        parser = PythonParser()
        source = "def bad syntax here"
        
        with pytest.raises(SyntaxError):
            parser.parse_file("test.py", source)


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestJavaScriptParser:
    """Test JavaScript/JSX parser (requires optional dependencies)"""
    
    def test_extensions(self):
        """Should handle JS file extensions"""
        from mcp_core.algorithms.parsers.javascript_parser import JavaScriptParser
        parser = JavaScriptParser()
        assert ".js" in parser.extensions
        assert ".jsx" in parser.extensions
        assert ".mjs" in parser.extensions
    
    def test_parse_function_declaration(self):
        """Should parse function declaration"""
        from mcp_core.algorithms.parsers.javascript_parser import JavaScriptParser
        parser = JavaScriptParser()
        source = '''
function greet(name) {
    console.log("Hello, " + name);
}
'''
        nodes = parser.parse_file("test.js", source)
        
        assert len(nodes) >= 1
        func_node = next(n for n in nodes if n.name == "greet")
        assert func_node.node_type == "function"
    
    def test_parse_arrow_function(self):
        """Should parse arrow function assigned to variable"""
        from mcp_core.algorithms.parsers.javascript_parser import JavaScriptParser
        parser = JavaScriptParser()
        source = '''
const add = (a, b) => a + b;
'''
        nodes = parser.parse_file("test.js", source)
        
        assert len(nodes) >= 1
        func_node = next(n for n in nodes if n.name == "add")
        assert func_node.node_type == "function"
    
    def test_parse_class(self):
        """Should parse class with inheritance"""
        from mcp_core.algorithms.parsers.javascript_parser import JavaScriptParser
        parser = JavaScriptParser()
        source = '''
class Rectangle extends Shape {
    constructor(width, height) {
        super();
        this.width = width;
    }
}
'''
        nodes = parser.parse_file("test.js", source)
        
        class_node = next(n for n in nodes if n.node_type == "class")
        assert class_node.name == "Rectangle"
        assert "Shape" in class_node.inherits


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestTypeScriptParser:
    """Test TypeScript/TSX parser (requires optional dependencies)"""
    
    def test_extensions(self):
        """Should handle TypeScript file extensions"""
        from mcp_core.algorithms.parsers.typescript_parser import TypeScriptParser
        parser = TypeScriptParser()
        assert ".ts" in parser.extensions
        assert ".tsx" in parser.extensions
    
    def test_parse_interface(self):
        """Should parse interface declaration (TypeScript-specific)"""
        from mcp_core.algorithms.parsers.typescript_parser import TypeScriptParser
        parser = TypeScriptParser()
        source = '''
interface Person {
    name: string;
    age: number;
}
'''
        nodes = parser.parse_file("test.ts", source)
        
        interface_node = next((n for n in nodes if n.node_type == "interface"), None)
        assert interface_node is not None
        assert interface_node.name == "Person"
    
    def test_parse_type_alias(self):
        """Should parse type alias (TypeScript-specific)"""
        from mcp_core.algorithms.parsers.typescript_parser import TypeScriptParser
        parser = TypeScriptParser()
        source = '''
type Point = { x: number; y: number };
'''
        nodes = parser.parse_file("test.ts", source)
        
        type_node = next((n for n in nodes if n.node_type == "type"), None)
        assert type_node is not None
        assert type_node.name == "Point"

