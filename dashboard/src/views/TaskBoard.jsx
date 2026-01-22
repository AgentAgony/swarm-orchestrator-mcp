import React, { useState } from 'react';
import { useSwarmData } from '../hooks/useSwarmData';
import TaskCard from '../components/TaskCard';
import { Filter, Plus } from 'lucide-react';

const TaskBoard = () => {
  const { data: tasks, loading, error } = useSwarmData('/tasks', 3000);
  const [filter, setFilter] = useState('ALL');
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [newTaskDesc, setNewTaskDesc] = useState('');

  const handleCreateTask = async () => {
    if (!newTaskDesc.trim()) return;
    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `description=${encodeURIComponent(newTaskDesc)}`
      });
      if (res.ok) {
        setShowNewTaskModal(false);
        setNewTaskDesc('');
        window.location.reload();
      } else {
        alert('Failed to create task');
      }
    } catch (e) {
      alert(`Error: ${e}`);
    }
  };

  if (loading) return <div className="page-content">Loading tasks...</div>;
  if (error) return <div className="page-content">Error loading tasks: {error}</div>;

  const filteredTasks = tasks ? tasks.filter(t => {
    if (filter === 'ALL') return true;
    return t.status === filter;
  }) : [];

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 className="gradient-text" style={{margin: 0}}>Task Board</h1>
        
        <div className="glass-panel" style={{ padding: '8px', display: 'flex', gap: '8px', borderRadius: '12px' }}>
          {['ALL', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'].map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              style={{
                background: filter === status ? 'rgba(255,255,255,0.1)' : 'transparent',
                border: 'none',
                color: filter === status ? '#fff' : 'var(--text-secondary)',
                padding: '8px 16px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.9rem',
                transition: 'all 0.2s'
              }}
            >
              {status === 'ALL' ? 'All Tasks' : status}
            </button>
          ))}
        </div>
        
        <button 
          onClick={() => setShowNewTaskModal(true)}
          className="glass-panel"
          style={{
            padding: '10px 18px',
            background: 'var(--accent-primary)',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontWeight: 600,
            borderRadius: '8px'
          }}
        >
          <Plus size={18} />
          New Task
        </button>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p>No tasks found with status: {filter}</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
          {filteredTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
      
      {/* New Task Modal */}
      {showNewTaskModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ padding: '32px', width: '500px', maxWidth: '90%' }}>
            <h2 style={{ marginBottom: '20px' }}>Create New Task</h2>
            <textarea
              value={newTaskDesc}
              onChange={(e) => setNewTaskDesc(e.target.value)}
              placeholder="Describe the task..."
              style={{
                width: '100%',
                minHeight: '120px',
                padding: '12px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-glass)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                fontFamily: 'inherit',
                fontSize: '1rem',
                resize: 'vertical'
              }}
            />
            <div style={{ display: 'flex', gap: '12px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowNewTaskModal(false)}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-primary)',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTask}
                style={{
                  padding: '10px 20px',
                  background: 'var(--accent-primary)',
                  border: 'none',
                  color: 'white',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskBoard;
