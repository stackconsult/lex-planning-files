"""Token Efficiency Dashboard Component.

Visualizes predictability curve, token savings, and forensic
consistency metrics in real-time.
"""
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TokenMetric {
  timestamp: string;
  complexity_score: number;
  tokens_per_operation: number;
  compression_ratio: number;
  forensic_score: number;
}

interface DashboardProps {
  apiEndpoint: string;
  refreshInterval?: number;
}

export const TokenEfficiencyDashboard: React.FC<DashboardProps> = ({
  apiEndpoint,
  refreshInterval = 5000,
}) => {
  const [metrics, setMetrics] = useState<TokenMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${apiEndpoint}/metrics/efficiency`);
        if (!response.ok) throw new Error('Failed to fetch metrics');
        const data = await response.json();
        setMetrics(data.data_points || []);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [apiEndpoint, refreshInterval]);

  if (loading) return <div>Loading metrics...</div>;
  if (error) return <div>Error: {error}</div>;

  const totalSavings = metrics.reduce((acc, m) => acc + (m.compression_ratio - 1) * 100, 0);
  const avgForensicScore = metrics.reduce((acc, m) => acc + m.forensic_score, 0) / metrics.length || 0;

  return (
    <div className="token-efficiency-dashboard">
      <h2>Token Efficiency Predictability Curve</h2>
      
      <div className="metrics-summary">
        <div className="metric-card">
          <h3>Total Token Savings</h3>
          <p>{totalSavings.toFixed(2)}%</p>
        </div>
        <div className="metric-card">
          <h3>Avg Forensic Score</h3>
          <p>{(avgForensicScore * 100).toFixed(1)}%</p>
        </div>
        <div className="metric-card">
          <h3>Data Points</h3>
          <p>{metrics.length}</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={metrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="complexity_score" label={{ value: 'System Complexity', position: 'bottom' }} />
          <YAxis label={{ value: 'Tokens / Operation', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="tokens_per_operation" 
            stroke="#8884d8" 
            name="Token Efficiency"
          />
          <Line 
            type="monotone" 
            dataKey="compression_ratio" 
            stroke="#82ca9d" 
            name="Compression Ratio"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TokenEfficiencyDashboard;
