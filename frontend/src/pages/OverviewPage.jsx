import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOverview } from '../api';
import MetricCard from '../components/MetricCard';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { Building2, Shield, AlertTriangle, EyeOff } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

const RISK_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#22c55e',
  UNASSESSED: '#64748b'
};

export default function OverviewPage({ batchId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await getOverview(batchId);
        setData(res.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch overview');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [batchId]);

  if (loading) return <LoadingSpinner message="Loading overview..." />;
  if (error) return <div className="p-6"><ErrorBanner message={error} /></div>;
  if (!data) return null;

  const rawDist = data.risk_distribution || {};
  const pieData = Object.entries(rawDist)
    .map(([key, val]) => ({
      name: key.toUpperCase(),
      value: val
    }))
    .filter(item => item.value > 0);

  const sectorList = Array.isArray(data.sector_breakdown) ? data.sector_breakdown : Object.values(data.sector_breakdown || {});
  const barData = sectorList.map(item => ({
    name: item.sector || 'Unknown',
    CRITICAL: item.critical || 0,
    HIGH: item.high || 0,
    MEDIUM: item.medium || 0,
    LOW: item.low || 0,
    UNASSESSED: item.unassessed || 0
  }));

  const topRisks = data.top_risks || data.top_risky_entities || [];
  const cseCount = data.cse_count ?? data.total_cses ?? 0;
  const alertCount = data.alert_count ?? data.total_alerts ?? 0;
  const attentionCount = data.entities_requiring_attention ?? (rawDist.critical || 0) + (rawDist.high || 0);
  const negativeSpaceCount = data.negative_space_count ?? data.negative_space_total ?? 0;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold">Batch Overview</h1>
          <p className="text-slate-400 mt-1 font-mono text-sm">Batch ID: {batchId}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <MetricCard title="CSEs Analysed" value={cseCount} icon={Building2} color="blue" />
        <MetricCard title="Total Alerts" value={alertCount.toLocaleString()} icon={Shield} color="slate" />
        <MetricCard title="Entities Requiring Attention" value={attentionCount} icon={AlertTriangle} color="red" />
        <MetricCard title="Negative Space Findings" value={negativeSpaceCount} icon={EyeOff} color="orange" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
        <div className="lg:col-span-3 bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h2 className="text-lg font-semibold mb-4">Risk Distribution</h2>
          <div className="h-80 w-full flex items-center justify-center">
            {pieData.length === 0 ? (
              <p className="text-slate-500 text-sm">No risk distribution data available.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={110}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Legend 
                    verticalAlign="middle" 
                    align="right" 
                    layout="vertical"
                    formatter={(value) => <span className="text-slate-300 font-medium text-xs ml-2 uppercase">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="lg:col-span-2 bg-slate-800 rounded-xl p-5 border border-slate-700 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Highest Risk Entities</h2>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-slate-400 border-b border-slate-700">
                <tr>
                  <th className="pb-2 font-medium">CSE ID</th>
                  <th className="pb-2 font-medium">Level</th>
                  <th className="pb-2 font-medium">Score</th>
                </tr>
              </thead>
              <tbody>
                {topRisks.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="py-6 text-center text-slate-500">No entities analyzed yet.</td>
                  </tr>
                ) : (
                  topRisks.slice(0, 5).map(entity => (
                    <tr 
                      key={entity.cse_id} 
                      className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer transition-colors"
                      onClick={() => navigate(`/entity/${entity.cse_id}`)}
                    >
                      <td className="py-3 font-mono text-blue-400 font-semibold">{entity.cse_id}</td>
                      <td className="py-3"><RiskBadge level={entity.risk_level} /></td>
                      <td className="py-3 font-semibold text-slate-100">{Number(entity.risk_score || 0).toFixed(1)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
        <h2 className="text-lg font-semibold mb-4">Sector Breakdown</h2>
        <div className="h-80 w-full">
          {barData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
              No sector breakdown data available.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <RechartsTooltip 
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                />
                <Legend formatter={(val) => <span className="text-slate-300 text-xs font-medium uppercase ml-1">{val}</span>} />
                <Bar dataKey="CRITICAL" stackId="a" fill={RISK_COLORS.CRITICAL} />
                <Bar dataKey="HIGH" stackId="a" fill={RISK_COLORS.HIGH} />
                <Bar dataKey="MEDIUM" stackId="a" fill={RISK_COLORS.MEDIUM} />
                <Bar dataKey="LOW" stackId="a" fill={RISK_COLORS.LOW} />
                <Bar dataKey="UNASSESSED" stackId="a" fill={RISK_COLORS.UNASSESSED} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
