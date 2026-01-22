import React from 'react';
import { RefreshCw, Database, Trash2, Zap, AlertOctagon } from 'lucide-react';
import { useSwarmData } from '../hooks/useSwarmData';

const QuickAction = ({ icon: Icon, label, description, onClick, color }) => (
  <button 
    onClick={onClick}
    className="glass-panel"
    style={{
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      background: 'rgba(255, 255, 255, 0.03)',
      border: '1px solid var(--border-glass)',
      cursor: 'pointer',
      textAlign: 'left',
      transition: 'all 0.2s ease',
      width: '100%'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = `rgba(${color}, 0.1)`;
      e.currentTarget.style.borderColor = `rgb(${color})`;
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
      e.currentTarget.style.borderColor = 'var(--border-glass)';
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: `rgb(${color})`, fontWeight: 700 }}>
      <Icon size={18} />
      {label}
    </div>
    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
      {description}
    </span>
  </button>
);

const QuickActionsPanel = () => {
    const triggerAction = async (endpoint, method='POST') => {
        try {
            const res = await fetch(`/api${endpoint}`, { method });
            if (res.ok) alert('Action triggered successfully');
            else alert('Action failed');
        } catch (e) {
            alert('Error triggering action: ' + e);
        }
    };

    return (
        <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                <Zap size={24} color="#f59e0b" />
                <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Quick Actions</h2>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <QuickAction 
                    icon={RefreshCw} 
                    label="Optimize DB" 
                    description="Run VACUUM / WAL" 
                    color="99, 102, 241"
                    onClick={() => triggerAction('/telemetry/optimize')}
                />
                <QuickAction 
                    icon={Trash2} 
                    label="Prune Telemetry" 
                    description="Delete events > 30 days" 
                    color="239, 68, 68"
                    onClick={() => triggerAction('/telemetry/prune')}
                />
                 <QuickAction 
                    icon={AlertOctagon} 
                    label="Reset Breakers" 
                    description="Clear all tool blocks" 
                    color="16, 185, 129"
                    onClick={() => alert('Feature coming soon')}
                />
            </div>
        </div>
    );
};

export default QuickActionsPanel;
