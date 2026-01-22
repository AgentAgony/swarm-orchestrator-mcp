import React from 'react';
import { Activity, AlertTriangle, ShieldCheck } from 'lucide-react';

const HealthBadge = ({ health }) => {
  const status = health?.status || 'loading';
  const color = 
    status === 'healthy' ? '#10b981' :
    status === 'critical' ? '#ef4444' :
    status === 'degraded' ? '#f59e0b' : '#6366f1';

  const icon = 
    status === 'healthy' ? <ShieldCheck size={16} color={color} /> :
    status === 'critical' ? <AlertTriangle size={16} color={color} /> :
    <Activity size={16} color={color} />;

  return (
    <div 
      className="glass-panel" 
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        borderRadius: '8px',
        background: `rgba(${status === 'healthy' ? '16, 185, 129' : status === 'critical' ? '239, 68, 68' : '99, 102, 241'}, 0.1)`,
        border: `1px solid ${color}40`,
        marginTop: '16px',
        marginBottom: '16px'
      }}
    >
      {icon}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>SYSTEM HEALTH</span>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color, textTransform: 'uppercase' }}>
          {status}
        </span>
      </div>
    </div>
  );
};

export default HealthBadge;
