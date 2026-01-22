import React, { useState, useEffect } from 'react';
import { Layers, ChevronDown, Check } from 'lucide-react';
import { useSwarmData } from '../hooks/useSwarmData';

const SessionSwitcher = () => {
    const { data: sessionData, loading } = useSwarmData('/sessions', 10000);
    const [isOpen, setIsOpen] = useState(false);
    const [activating, setActivating] = useState(null);

    const activeSession = sessionData?.active_session;
    const sessions = sessionData?.sessions || [];

    const switchSession = async (sessionId) => {
        if (sessionId === activeSession) return;
        setActivating(sessionId);
        try {
            const res = await fetch(`/api/sessions/${sessionId}/activate`, { method: 'POST' });
            if (res.ok) {
                // Hard reload to reset all dashboard states for the new session
                window.location.reload();
            } else {
                alert('Failed to switch session');
            }
        } catch (e) {
            alert('Error switching session: ' + e);
        } finally {
            setActivating(null);
            setIsOpen(false);
        }
    };

    if (loading && !sessionData) return null;

    return (
        <div style={{ position: 'relative', marginTop: '12px' }}>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="glass-panel"
                style={{
                    width: '100%',
                    padding: '10px 12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-glass)',
                    cursor: 'pointer',
                    borderRadius: '8px'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers size={16} color="var(--accent-primary)" />
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {activeSession || 'Default'}
                    </span>
                </div>
                <ChevronDown size={14} color="var(--text-secondary)" style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
            </button>

            {isOpen && (
                <div className="glass-panel" style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    marginTop: '8px',
                    zIndex: 100,
                    maxHeight: '200px',
                    overflowY: 'auto',
                    padding: '8px',
                    background: 'rgba(15, 23, 42, 0.95)',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)'
                }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 700, padding: '4px 8px', marginBottom: '4px' }}>
                        ACTIVE SESSIONS
                    </div>
                    {sessions.map((s) => (
                        <button
                            key={s.session_id}
                            onClick={() => switchSession(s.session_id)}
                            style={{
                                width: '100%',
                                padding: '8px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                background: s.session_id === activeSession ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                textAlign: 'left',
                                color: s.session_id === activeSession ? 'var(--accent-primary)' : 'var(--text-primary)',
                                transition: 'background 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
                            onMouseOut={(e) => e.currentTarget.style.background = s.session_id === activeSession ? 'rgba(99, 102, 241, 0.1)' : 'transparent'}
                        >
                            <span style={{ fontSize: '0.8rem', fontWeight: s.session_id === activeSession ? 700 : 500 }}>
                                {s.session_id}
                            </span>
                            {s.session_id === activeSession && <Check size={14} />}
                            {activating === s.session_id && <div className="spin" style={{ width: '12px', height: '12px', border: '2px solid white', borderTop: '2px solid transparent', borderRadius: '50%' }}></div>}
                        </button>
                    ))}
                    <div style={{ borderTop: '1px solid var(--border-glass)', marginTop: '8px', paddingTop: '8px' }}>
                         <button
                            onClick={() => {
                                const name = prompt('Enter new session name:');
                                if (name) switchSession(name);
                            }}
                            style={{
                                width: '100%',
                                padding: '8px',
                                background: 'transparent',
                                border: '1px dashed var(--border-glass)',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                color: 'var(--text-secondary)',
                                fontSize: '0.75rem'
                            }}
                        >
                            + Start New Session
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SessionSwitcher;
