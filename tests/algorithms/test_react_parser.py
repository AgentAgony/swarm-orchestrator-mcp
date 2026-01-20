"""
Tests for React/Next.js component detection in JavaScript parser.

Tests component detection, JSX rendering extraction, Next.js patterns, and hooks.
"""

import pytest
from mcp_core.algorithms.parsers import JavaScriptParser


def _treesitter_available() -> bool:
    """Check if Tree-sitter packages are installed"""
    try:
        import tree_sitter
        import tree_sitter_javascript
        return True
    except ImportError:
        return False


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestReactComponentDetection:
    """Test React component detection heuristics"""
    
    def test_identifies_react_component(self):
        """Should identify function returning JSX as component"""
        parser = JavaScriptParser()
        source = '''
function Button({ label }) {
    return <button>{label}</button>;
}
'''
        nodes = parser.parse_file("Button.jsx", source)
        
        assert len(nodes) == 1
        assert nodes[0].node_type == "component"
        assert nodes[0].name == "Button"
    
    def test_regular_function_not_component(self):
        """Should NOT identify regular function as component"""
        parser = JavaScriptParser()
        source = '''
function calculate(a, b) {
    return a + b;
}
'''
        nodes = parser.parse_file("utils.js", source)
        
        assert len(nodes) == 1
        assert nodes[0].node_type == "function"
        assert nodes[0].name == "calculate"
    
    def test_lowercase_with_jsx_not_component(self):
        """Lowercase function with JSX should be function, not component"""
        parser = JavaScriptParser()
        source = '''
function renderHelper() {
    return <div>Helper</div>;
}
'''
        nodes = parser.parse_file("helper.js", source)
        
        # Lowercase = not a React component (convention)
        assert nodes[0].node_type == "function"
        assert nodes[0].name == "renderHelper"
    
    def test_arrow_function_component(self):
        """Should identify arrow function component"""
        parser = JavaScriptParser()
        source = '''
const Header = () => {
    return <header>Title</header>;
};
'''
        nodes = parser.parse_file("Header.jsx", source)
        
        assert len(nodes) == 1
        assert nodes[0].node_type == "component"
        assert nodes[0].name == "Header"


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestJSXRendering:
    """Test JSX component rendering extraction"""
    
    def test_extracts_jsx_component_usage(self):
        """Should extract components used in JSX"""
        parser = JavaScriptParser()
        source = '''
function Navbar() {
    return (
        <div>
            <Logo />
            <SearchBar />
            <UserMenu />
        </div>
    );
}
'''
        nodes = parser.parse_file("Navbar.jsx", source)
        
        assert nodes[0].renders == ['Logo', 'SearchBar', 'UserMenu']
    
    def test_ignores_html_tags(self):
        """Should NOT track lowercase HTML tags"""
        parser = JavaScriptParser()
        source = '''
function Card() {
    return (
        <div>
            <h1>Title</h1>
            <Button />
        </div>
    );
}
'''
        nodes = parser.parse_file("Card.jsx", source)
        
        # Only uppercase components tracked
        assert nodes[0].renders == ['Button']
        assert 'div' not in nodes[0].renders
        assert 'h1' not in nodes[0].renders
    
    def test_self_closing_tags(self):
        """Should handle self-closing JSX tags"""
        parser = JavaScriptParser()
        source = '''
function Profile() {
    return <Avatar size="large" />;
}
'''
        nodes = parser.parse_file("Profile.jsx", source)
        
        assert nodes[0].renders == ['Avatar']
    
    def test_nested_components(self):
        """Should extract deeply nested components"""
        parser = JavaScriptParser()
        source = '''
function Dashboard() {
    return (
        <Layout>
            <Sidebar>
                <NavItem />
                <NavItem />
            </Sidebar>
            <Content>
                <Chart />
            </Content>
        </Layout>
    );
}
'''
        nodes = parser.parse_file("Dashboard.jsx", source)
        
        # Set removes duplicates
        renders = set(nodes[0].renders)
        assert renders == {'Layout', 'Sidebar', 'NavItem', 'Content', 'Chart'}


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestNextJSPatterns:
    """Test Next.js file-based routing detection"""
    
    def test_detects_pages_router_page(self):
        """Should detect Pages Router page component"""
        parser = JavaScriptParser()
        source = '''
export default function HomePage() {
    return <div>Home</div>;
}
'''
        nodes = parser.parse_file("pages/index.tsx", source)
        
        assert nodes[0].framework_role == "next_page"
    
    def test_detects_app_router_page(self):
        """Should detect App Router page component"""
        parser = JavaScriptParser()
        source = '''
export default function Page() {
    return <div>Page</div>;
}
'''
        nodes = parser.parse_file("app/dashboard/page.tsx", source)
        
        assert nodes[0].framework_role == "next_app_route"
    
    def test_detects_app_router_layout(self):
        """Should detect App Router layout component"""
        parser = JavaScriptParser()
        source = '''
export default function RootLayout({ children }) {
    return <html><body>{children}</body></html>;
}
'''
        nodes = parser.parse_file("app/layout.tsx", source)
        
        assert nodes[0].framework_role == "next_layout"
    
    def test_detects_api_route(self):
        """Should detect Pages Router API route"""
        parser = JavaScriptParser()
        source = '''
function handler(req, res) {
    res.json({ data: 'test' });
}
'''
        # API routes are lowercase functions
        nodes = parser.parse_file("pages/api/users.ts", source)
        
        assert nodes[0].framework_role == "next_api_route"
    
    def test_detects_app_router_api_handler(self):
        """Should detect App Router API route handler"""
        parser = JavaScriptParser()
        source = '''
function GET(request) {
    return new Response('Hello');
}
'''
        nodes = parser.parse_file("app/api/route.ts", source)
        
        assert nodes[0].framework_role == "next_api_handler"
    
    def test_non_nextjs_file_has_no_role(self):
        """Regular files should have no framework role"""
        parser = JavaScriptParser()
        source = '''
function Component() {
    return <div />;
}
'''
        nodes = parser.parse_file("src/components/Component.jsx", source)
        
        assert nodes[0].framework_role is None


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestReactHooks:
    """Test React hooks detection"""
    
    def test_detects_useState(self):
        """Should detect useState hook"""
        parser = JavaScriptParser()
        source = '''
function Counter() {
    const [count, setCount] = useState(0);
    return <div>{count}</div>;
}
'''
        nodes = parser.parse_file("Counter.jsx", source)
        
        assert 'useState' in nodes[0].metadata['hooks']
    
    def test_detects_multiple_hooks(self):
        """Should detect multiple hooks"""
        parser = JavaScriptParser()
        source = '''
function DataFetcher() {
    const [data, setData] = useState(null);
    useEffect(() => {
        fetchData();
    }, []);
    
    return <div>{data}</div>;
}
'''
        nodes = parser.parse_file("DataFetcher.jsx", source)
        
        hooks = nodes[0].metadata['hooks']
        assert 'useState' in hooks
        assert 'useEffect' in hooks
    
    def test_detects_custom_hooks(self):
        """Should detect custom hooks (useXxx pattern)"""
        parser = JavaScriptParser()
        source = '''
function Profile() {
    const user = useAuth();
    const theme = useTheme();
    return <div />;
}
'''
        nodes = parser.parse_file("Profile.jsx", source)
        
        hooks = nodes[0].metadata['hooks']
        assert 'useAuth' in hooks
        assert 'useTheme' in hooks
    
    def test_non_component_no_hooks(self):
        """Regular functions shouldn't have hooks metadata"""
        parser = JavaScriptParser()
        source = '''
function calculate() {
    const result = useState(0);  // Not actually a hook here
    return result;
}
'''
        nodes = parser.parse_file("utils.js", source)
        
        # Regular function, so no hooks extracted
        assert 'hooks' not in nodes[0].metadata


@pytest.mark.skipif(
    not _treesitter_available(),
    reason="Tree-sitter packages not installed"
)
class TestIntegration:
    """Test full integration scenarios"""
    
    def test_full_react_component_analysis(self):
        """Should extract all React data for a complex component"""
        parser = JavaScriptParser()
        source = '''
function TodoList({ items }) {
    const [filter, setFilter] = useState('all');
    useEffect(() => {
        console.log('Filter changed');
    }, [filter]);
    
    return (
        <Container>
            <FilterBar onFilterChange={setFilter} />
            <TodoItem items={items} />
            <AddButton />
        </Container>
    );
}
'''
        nodes = parser.parse_file("app/TodoList.jsx", source)
        
        assert nodes[0].node_type == "component"
        assert nodes[0].name == "TodoList"
        assert set(nodes[0].renders) == {'Container', 'FilterBar', 'TodoItem', 'AddButton'}
        assert 'useState' in nodes[0].metadata['hooks']
        assert 'useEffect' in nodes[0].metadata['hooks']
        assert 'setFilter' in nodes[0].calls  # Event handler calls
