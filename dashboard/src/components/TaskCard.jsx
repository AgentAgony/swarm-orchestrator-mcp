import React, { useState } from 'react';
import { X, RefreshCw, Loader, Clock, CheckCircle, AlertCircle } from 'lucide-react';

const TaskCard = ({ task }) => {
  const [actionLoading, setActionLoading] = useState(false);

  const handleAction = async (action) => {
    setActionLoading(true);
    try {
      const res = await fetch(`/api/tasks/${task.task_id}/${action}`, { method: 'POST' });
      if (res.ok) {
        alert(`Task ${action} successful`);
        window.location.reload();
      } else {
        alert(`Failed to ${action} task`);
      }
    } catch (e) {
      alert(`Error: ${e}`);
    } finally {
      setActionLoading(false);
    }
  };

  const statusConfig = {
    'COMPLETED': { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', icon: CheckCircle },
    'FAILED': { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', icon: AlertCircle },
    'RUNNING': { color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)', icon: Loader },
    'PENDING': { color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.1)', icon: Clock }
  };

  const config = statusConfig[task.status] || statusConfig['PENDING'];
  const StatusIcon = config.icon;

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <StatusIcon size={16} color={config.color} />
            <span style={{
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: 700,
              background: config.bg,
              color: config.color
            }}>
              {task.status}
            </span>
          </div>
          <p style={{ margin: '8px 0 4px 0', fontSize: '1rem', fontWeight: 600 }}>{task.description}</p>
          <code style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{task.task_id}</code>
        </div>
      </div>

      {task.feedback_log && task.feedback_log.length > 0 && (
        <div style={{ 
          marginTop: '8px', 
          padding: '8px 12px', 
          background: 'rgba(255, 255, 255, 0.03)', 
          borderRadius: '6px',
          fontSize: '0.85rem', 
          color: 'var(--text-secondary)' 
        }}>
          {task.feedback_log[task.feedback_log.length - 1]}
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
        {task.status === 'RUNNING' && (
          <button
            onClick={() => handleAction('cancel')}
            disabled={actionLoading}
            style={{
              flex: 1,
              padding: '8px 16px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#ef4444',
              borderRadius: '6px',
              cursor: actionLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontWeight: 600
            }}
          >
            {actionLoading ? <Loader size={14} className="spin" /> : <X size={14} />}
            Cancel
          </button>
        )}
        
        {task.status === 'FAILED' && (
          <button
            onClick={() => handleAction('retry')}
            disabled={actionLoading}
            style={{
              flex: 1,
              padding: '8px 16px',
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              color: '#6366f1',
              borderRadius: '6px',
              cursor: actionLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontWeight: 600
            }}
          >
            {actionLoading ? <Loader size={14} className="spin" /> : <RefreshCw size={14} />}
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
