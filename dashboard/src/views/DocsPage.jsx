import React from 'react';
import { Book, Github, Zap, Shield, Cpu, Network } from 'lucide-react';

const DocsPage = () => {
  return (
    <div className="page-content">
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {/* Hero Section */}
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h1 className="gradient-text" style={{ fontSize: '3rem', marginBottom: '16px' }}>
            Swarm Orchestrator
          </h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Multi-Agent Task Orchestration with Algorithmic Intelligence
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <a 
              href="https://github.com/AgentAgony/swarm" 
              target="_blank" 
              rel="noopener noreferrer"
              className="glass-panel"
              style={{ 
                padding: '12px 24px', 
                textDecoration: 'none', 
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontWeight: 600
              }}
            >
              <Github size={20} />
              View on GitHub
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '48px' }}>
          <div className="glass-panel" style={{ padding: '24px' }}>
            <Zap size={32} color="#6366f1" style={{ marginBottom: '12px' }} />
            <h3 style={{ marginBottom: '8px' }}>Fast Indexing</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Multi-threaded codebase indexing with HippoRAG graph persistence
            </p>
          </div>
          
          <div className="glass-panel" style={{ padding: '24px' }}>
            <Network size={32} color="#a855f7" style={{ marginBottom: '12px' }} />
            <h3 style={{ marginBottom: '8px' }}>Knowledge Graph</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              AST-based dependency analysis with PageRank retrieval
            </p>
          </div>
          
          <div className="glass-panel" style={{ padding: '24px' }}>
            <Cpu size={32} color="#ec4899" style={{ marginBottom: '12px' }} />
            <h3 style={{ marginBottom: '8px' }}>Algorithmic Workers</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Debate Engine, Git Worker, CRDT Merger, and more
            </p>
          </div>
        </div>

        {/* Quick Start */}
        <div className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
          <h2 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Book size={28} />
            Quick Start
          </h2>
          
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Installation</h3>
            <pre style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '16px', 
              borderRadius: '8px', 
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
{`# Clone the repository
git clone https://github.com/AgentAgony/swarm.git
cd swarm

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY or OPENAI_API_KEY`}
            </pre>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Running the MCP Server</h3>
            <pre style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '16px', 
              borderRadius: '8px',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
{`# Start the MCP server (Stdio mode for IDE integration)
python server.py

# Or use Docker
docker-compose up -d`}
            </pre>
          </div>

          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Running the Dashboard</h3>
            <pre style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '16px', 
              borderRadius: '8px',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
{`# Build the dashboard
cd dashboard
npm install
npm run build

# Start the dashboard server
cd ..
python dashboard_server.py

# Access at http://localhost:8000`}
            </pre>
          </div>
        </div>

        {/* Key Features */}
        <div className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
          <h2 style={{ marginBottom: '24px' }}>Key Features</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: '#6366f1' }}>
                🔍 Hybrid Search Engine
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Semantic + keyword search with API-based embeddings (Gemini/OpenAI) or offline mode
              </p>
            </div>
            
            <div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: '#a855f7' }}>
                🧠 HippoRAG Context Retrieval
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                AST-based knowledge graphs with Personalized PageRank for deep code understanding
              </p>
            </div>
            
            <div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: '#ec4899' }}>
                🤖 Structured Deliberation
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Multi-step reasoning with algorithmic workers (Debate, Voting, Ochiai Localization)
              </p>
            </div>
            
            <div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: '#22c55e' }}>
                📊 Real-Time Dashboard
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Monitor tasks, visualize knowledge graphs, and track system health
              </p>
            </div>
          </div>
        </div>

        {/* Architecture */}
        <div className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
          <h2 style={{ marginBottom: '16px' }}>Architecture</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Swarm follows a modular architecture with clear separation of concerns. The diagram below illustrates the high-level system design.
          </p>
          
          <div className="glass-panel" style={{ height: '400px', marginBottom: '24px', background: 'rgba(0,0,0,0.2)', overflow: 'hidden' }}>
             <ArchitectureGraph />
          </div>

          <ul style={{ color: 'var(--text-secondary)', lineHeight: '1.8', paddingLeft: '24px' }}>
            <li><strong>MCP Server</strong> - FastMCP-based server exposing tools via Model Context Protocol</li>
            <li><strong>Orchestrator</strong> - Task routing and state management with blackboard pattern</li>
            <li><strong>Algorithms</strong> - Pluggable workers (HippoRAG, Debate, Git, CRDT, Z3)</li>
            <li><strong>Search Engine</strong> - Hybrid semantic/keyword search with caching</li>
            <li><strong>Dashboard</strong> - React frontend with FastAPI backend bridge</li>
          </ul>
        </div>
        
        {/* Links */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {/* ... existing links ... */}
          <a 
            href="https://github.com/AgentAgony/swarm/blob/main/README.md" 
            target="_blank"
            rel="noopener noreferrer"
            className="glass-panel"
            style={{ 
              padding: '20px', 
              textDecoration: 'none', 
              color: 'var(--text-primary)',
              textAlign: 'center'
            }}
          >
            <h4>Full Documentation</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              Complete setup guide
            </p>
          </a>
          
          <a 
            href="https://github.com/AgentAgony/swarm/blob/main/ARCHITECTURE.md" 
            target="_blank"
            rel="noopener noreferrer"
            className="glass-panel"
            style={{ 
              padding: '20px', 
              textDecoration: 'none', 
              color: 'var(--text-primary)',
              textAlign: 'center'
            }}
          >
            <h4>Architecture</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              System design details
            </p>
          </a>
          
          <a 
            href="https://github.com/AgentAgony/swarm/blob/main/CONTRIBUTING.md" 
            target="_blank"
            rel="noopener noreferrer"
            className="glass-panel"
            style={{ 
              padding: '20px', 
              textDecoration: 'none', 
              color: 'var(--text-primary)',
              textAlign: 'center'
            }}
          >
            <h4>Contributing</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              How to contribute
            </p>
          </a>
        </div>
      </div>
    </div>
  );
};

// Simple internal component for the architecture graph
import ForceGraph2D from 'react-force-graph-2d';
import { MOCK_ARCHITECTURE } from '../mockData';
import { useRef, useEffect, useState } from 'react';

const ArchitectureGraph = () => {
    const graphRef = useRef();
    const [width, setWidth] = useState(600);
    const containerRef = useRef(null);
    
    useEffect(() => {
        if(containerRef.current) {
            setWidth(containerRef.current.clientWidth);
        }
    }, []);

    return (
        <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
            <ForceGraph2D
                ref={graphRef}
                width={width}
                height={400}
                graphData={MOCK_ARCHITECTURE}
                nodeLabel="name"
                nodeColor={node => {
                    switch(node.type) {
                        case 'client': return '#f472b6';
                        case 'frontend': return '#a855f7';
                        case 'infrastructure': return '#94a3b8';
                        case 'service': return '#3b82f6';
                        case 'database': return '#22c55e';
                        default: return '#64748b';
                    }
                }}
                nodeVal={node => node.val}
                linkColor={() => 'rgba(255,255,255,0.2)'}
                backgroundColor="rgba(0,0,0,0)"
            />
        </div>
    );
};

export default DocsPage;
