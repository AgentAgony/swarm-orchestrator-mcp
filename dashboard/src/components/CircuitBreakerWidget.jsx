import React, { useState } from 'react';
import { AlertTriangle, RefreshCw, CheckCircle } from 'lucide-react';
import { useSwarmData } from '../hooks/useSwarmData';

const CircuitBreakerWidget = () => {
  const { data: breakers, loading, error } = useSwarmData('/circuit-breakers', 5000);
  const [resetting, setResetting] = useState(null);

  const handleReset = async (tool) => {
    setResetting(tool);
    try {
      await fetch(`/api/circuit-breakers/${tool}/reset`, { method: 'POST' });
      // In a real app we'd optimistically update or refetch
      alert(`Reset request sent for ${tool}`);
    } catch (e) {
      alert(`Failed to reset: ${e}`);
    } finally {
      setResetting(null);
    }
  };

  if (loading || !breakers || breakers.length === 0) return null;

  const tripped = breakers.filter(b => b.status === "TRIPPED");
  
  if (tripped.length === 0) return null; // Don't show if all good

  return (
    <div className="glass-panel" style={{ padding: '24px', marginTop: '24px', border: '1px solid rgba(239, 68, 68, 0.3)', background: 'rgba(239, 68, 68, 0.05)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <AlertTriangle size={24} color="#ef4444" />
        <h2 style={{ margin: 0, fontSize: '1.3rem', color: '#ef4444' }}>Circuit Breakers Tripped</h2>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {tripped.map((b) => (
          <div key={b.tool} className="glass-panel" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.2)' }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{b.tool}</div>
              <div style={{ color: '#ef4444', fontSize: '0.9rem' }}>Success Rate: {Math.round(b.success_rate * 100)}%</div>
            </div>
            
            <button 
              onClick={() => handleReset(b.tool)}
              disabled={resetting === b.tool}
              style={{
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {resetting === b.tool ? <RefreshCw size={14} className="spin" /> : <RefreshCw size={14} />}
              Reset
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CircuitBreakerWidget;
