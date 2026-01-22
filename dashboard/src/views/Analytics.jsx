import React from 'react';
import { AlertTriangle, CheckCircle, TrendingUp, Gauge } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import StatCard from '../components/StatCard';
import { useSwarmData } from '../hooks/useSwarmData';

const Analytics = () => {
  const { data: toolData, loading: toolLoading } = useSwarmData('/analytics/tools?days=7', 10000);
  const { data: roleData, loading: roleLoading } = useSwarmData('/analytics/roles', 10000);

  const loading = toolLoading || roleLoading;

  // Transform role data for chart
  const roleChartData = roleData?.map(r => ({
    name: r.role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    rate: Math.round(r.success_rate * 100),
    fill: r.success_rate >= 0.8 ? '#22c55e' : r.success_rate >= 0.5 ? '#f59e0b' : '#ef4444'
  })) || [];

  // Transform tool data for display  
  const problematicTools = toolData?.filter(t => t.success_rate < 0.8) || [];
  const healthyToolCount = (toolData?.length || 0) - problematicTools.length;
  const avgSuccessRate = toolData?.length 
    ? Math.round(toolData.reduce((acc, t) => acc + t.success_rate, 0) / toolData.length * 100)
    : 100;

  if (loading) {
    return <div className="page-content">Loading analytics data...</div>;
  }

  return (
    <div className="page-content">
      <h1 className="gradient-text">Telemetry Analytics</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
        Real-time performance insights from your local telemetry database
      </p>

      {/* Stats Overview */}
      <div className="stats-grid">
        <StatCard 
          icon={Gauge} 
          label="Avg Success Rate" 
          value={`${avgSuccessRate}%`}
          color={avgSuccessRate >= 80 ? '#22c55e' : '#f59e0b'}
          delay={0}
        />
        <StatCard 
          icon={CheckCircle} 
          label="Healthy Tools" 
          value={healthyToolCount}
          color="#22c55e"
          delay={0.1}
        />
        <StatCard 
          icon={AlertTriangle} 
          label="Problematic Tools" 
          value={problematicTools.length}
          color={problematicTools.length > 0 ? '#ef4444' : '#22c55e'}
          delay={0.2}
        />
        <StatCard 
          icon={TrendingUp} 
          label="Roles Tracked" 
          value={roleData?.length || 0}
          color="#6366f1"
          delay={0.3}
        />
      </div>

      {/* Role Performance Chart */}
      <div className="glass-panel dashboard-chart">
        <h2 style={{ marginBottom: '20px' }}>Git Role Success Rates</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={roleChartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" unit="%" />
              <YAxis type="category" dataKey="name" stroke="#94a3b8" width={120} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e2029', 
                  border: '1px solid rgba(255,255,255,0.1)', 
                  borderRadius: '8px' 
                }}
                itemStyle={{ color: '#f8fafc' }}
                formatter={(value) => [`${value}%`, 'Success Rate']}
              />
              <Bar dataKey="rate" radius={[0, 4, 4, 0]}>
                {roleChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Problematic Tools List */}
      {problematicTools.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
          <h2 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} color="#ef4444" />
            Unstable Tools
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', fontSize: '0.9rem' }}>
            These tools have been failing recently. The system will warn LLMs to use alternatives.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {problematicTools.map((tool, idx) => (
              <div 
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  borderRadius: '8px',
                  border: '1px solid rgba(239, 68, 68, 0.2)'
                }}
              >
                <code style={{ color: '#f8fafc' }}>{tool.tool}</code>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                    {tool.total_uses} uses
                  </span>
                  <span style={{ 
                    color: '#ef4444', 
                    fontWeight: 'bold',
                    background: 'rgba(239, 68, 68, 0.2)',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}>
                    {Math.round(tool.success_rate * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Issues State */}
      {problematicTools.length === 0 && (
        <div className="glass-panel" style={{ padding: '24px', marginTop: '24px', textAlign: 'center' }}>
          <CheckCircle size={48} color="#22c55e" style={{ marginBottom: '16px' }} />
          <h3 style={{ marginBottom: '8px' }}>All Systems Healthy</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            No tools are currently experiencing issues.
          </p>
        </div>
      )}
    </div>
  );
};

export default Analytics;
