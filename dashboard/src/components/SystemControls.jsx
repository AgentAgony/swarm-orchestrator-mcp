import React, { useState } from 'react';
import { Database, Network, Loader, FileText } from 'lucide-react';
import { useSwarmData } from '../hooks/useSwarmData';

const IndexingPanel = () => {
  const [indexing, setIndexing] = useState(false);
  const [graphing, setGraphing] = useState(false);

  const triggerIndexing = async () => {
    setIndexing(true);
    try {
      const res = await fetch('/api/indexing/codebase', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert(`Indexed ${data.chunks_indexed} chunks`);
      } else {
        alert('Indexing failed');
      }
    } catch (e) {
      alert(`Error: ${e}`);
    } finally {
      setIndexing(false);
    }
  };

  const triggerGraphRebuild = async () => {
    setGraphing(true);
    try {
      const res = await fetch('/api/indexing/graph', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert(`Graph rebuilt with ${data.nodes} nodes`);
      } else {
        alert('Graph rebuild failed');
      }
    } catch (e) {
      alert(`Error: ${e}`);
    } finally {
      setGraphing(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Database size={24} color="#a855f7" />
        <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Indexing Controls</h2>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
        <button
          onClick={triggerIndexing}
          disabled={indexing}
          className="glass-panel"
          style={{
            padding: '16px',
            background: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            cursor: indexing ? 'not-allowed' : 'pointer',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a855f7', fontWeight: 700 }}>
            {indexing ? <Loader size={18} className="spin" /> : <FileText size={18} />}
            Re-index Codebase
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Rebuild semantic search index
          </span>
        </button>
        
        <button
          onClick={triggerGraphRebuild}
          disabled={graphing}
          className="glass-panel"
          style={{
            padding: '16px',
            background: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            cursor: graphing ? 'not-allowed' : 'pointer',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a855f7', fontWeight: 700 }}>
            {graphing ? <Loader size={18} className="spin" /> : <Network size={18} />}
            Rebuild Knowledge Graph
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Regenerate HippoRAG graph
          </span>
        </button>
      </div>
    </div>
  );
};

const LogViewer = () => {
  const { data: logData } = useSwarmData('/logs?lines=30&level=ALL', 5000);

  return (
    <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <FileText size={24} color="#22d3ee" />
        <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Recent Logs</h2>
      </div>
      
      <div style={{
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '8px',
        padding: '16px',
        maxHeight: '300px',
        overflowY: 'auto',
        fontFamily: 'monospace',
        fontSize: '0.85rem'
      }}>
        {logData && logData.logs && logData.logs.length > 0 ? (
          logData.logs.map((line, idx) => (
            <div key={idx} style={{ marginBottom: '4px', color: 'var(--text-secondary)' }}>
              {line}
            </div>
          ))
        ) : (
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
            {logData?.message || 'No logs available'}
          </div>
        )}
      </div>
    </div>
  );
};

export { IndexingPanel, LogViewer };
