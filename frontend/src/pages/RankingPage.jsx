import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getEntities } from '../api';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

export default function RankingPage({ batchId }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [filterLevel, setFilterLevel] = useState('All');
  const [filterSector, setFilterSector] = useState('All');
  
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await getEntities(batchId);
        const list = Array.isArray(res.data) ? res.data : (res.data.entities || []);
        setEntities(list);
      } catch (err) {
        setError(err.message || 'Failed to fetch entities');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [batchId]);

  const sectors = useMemo(() => {
    const set = new Set(entities.map(e => e.sector).filter(Boolean));
    return ['All', ...Array.from(set)];
  }, [entities]);

  const filteredEntities = useMemo(() => {
    let result = [...entities];
    
    if (filterLevel !== 'All') {
      result = result.filter(e => e.risk_level === filterLevel);
    }
    
    if (filterSector !== 'All') {
      result = result.filter(e => e.sector === filterSector);
    }
    
    // Sort: unassessed (grey) at bottom, otherwise by risk score descending
    result.sort((a, b) => {
      if (a.is_grey && !b.is_grey) return 1;
      if (!a.is_grey && b.is_grey) return -1;
      return (b.risk_score || 0) - (a.risk_score || 0);
    });
    
    return result;
  }, [entities, filterLevel, filterSector]);

  if (loading) return <LoadingSpinner message="Loading queue..." />;

  const levels = ['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNASSESSED'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Risk Ranking Queue</h1>
      
      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
      
      <div className="flex flex-wrap gap-6 mb-6 items-center bg-slate-800/60 p-4 rounded-xl border border-slate-700">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Risk Level:</span>
          <div className="flex flex-wrap gap-1.5">
            {levels.map(lvl => (
              <button
                key={lvl}
                onClick={() => setFilterLevel(lvl)}
                className={`px-3 py-1 rounded-md text-xs font-semibold uppercase transition-colors ${
                  filterLevel === lvl 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-slate-900/80 text-slate-300 border border-slate-700 hover:bg-slate-700'
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>

        {sectors.length > 2 && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Sector:</span>
            <div className="flex flex-wrap gap-1.5">
              {sectors.map(sec => (
                <button
                  key={sec}
                  onClick={() => setFilterSector(sec)}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
                    filterSector === sec 
                      ? 'bg-blue-600 text-white shadow-sm' 
                      : 'bg-slate-900/80 text-slate-300 border border-slate-700 hover:bg-slate-700'
                  }`}
                >
                  {sec}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        {filteredEntities.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            No entities found in this batch matching selected filters.
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-700 uppercase text-xs font-semibold">
              <tr>
                <th className="p-4">CSE ID</th>
                <th className="p-4">Sector</th>
                <th className="p-4">Risk Score</th>
                <th className="p-4">Risk Level</th>
                <th className="p-4">Primary Finding</th>
                <th className="p-4 text-center">Flags</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntities.map((entity) => {
                const isUnassessed = entity.risk_level === 'UNASSESSED' || entity.is_grey;
                const score = entity.risk_score || 0;
                
                let barColor = 'bg-slate-500';
                if (entity.risk_level === 'CRITICAL') barColor = 'bg-red-500';
                else if (entity.risk_level === 'HIGH') barColor = 'bg-orange-500';
                else if (entity.risk_level === 'MEDIUM') barColor = 'bg-yellow-500';
                else if (entity.risk_level === 'LOW') barColor = 'bg-green-500';

                return (
                  <tr 
                    key={entity.cse_id} 
                    onClick={() => navigate(`/entity/${entity.cse_id}`)}
                    className={`border-b border-slate-700/50 hover:bg-slate-700/40 cursor-pointer transition-colors ${isUnassessed ? 'opacity-60 bg-slate-900/30' : ''}`}
                  >
                    <td className={`p-4 font-mono ${isUnassessed ? 'italic text-slate-400' : 'text-blue-400 font-bold'}`}>
                      {entity.cse_id}
                    </td>
                    <td className="p-4 text-slate-300">{entity.sector || 'Unknown'}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <span className="w-10 font-bold text-slate-100">{score.toFixed(1)}</span>
                        <div className="w-24 bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-700/50">
                          <div className={`h-full ${barColor}`} style={{ width: `${Math.min(score, 100)}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <RiskBadge level={entity.risk_level} />
                    </td>
                    <td className="p-4 text-slate-300 text-xs max-w-xs truncate" title={entity.primary_reason}>
                      {entity.primary_reason || '—'}
                    </td>
                    <td className="p-4 text-center">
                      <span className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-full text-xs font-mono text-slate-300 font-semibold">
                        {entity.flag_count ?? 0}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button className="bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600 hover:text-white px-3 py-1 rounded text-xs font-medium transition-colors">
                        View Dossier
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
