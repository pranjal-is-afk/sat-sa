import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getEntity, addNote } from '../api';
import RiskBadge from '../components/RiskBadge';
import ScoreBar from '../components/ScoreBar';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function DrilldownPage({ batchId }) {
  const { cseId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [noteInput, setNoteInput] = useState('');
  const [savingNote, setSavingNote] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await getEntity(cseId, batchId);
        setData(res.data);
        setNoteInput(res.data.supervisor_note || '');
      } catch (err) {
        setError(err.message || 'Failed to fetch entity details');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [cseId, batchId]);

  const handleSaveNote = async () => {
    try {
      setSavingNote(true);
      await addNote(batchId, cseId, noteInput);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to save note');
    } finally {
      setSavingNote(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading entity dossier..." />;
  if (error) return <div className="p-6"><ErrorBanner message={error} /></div>;
  if (!data) return null;

  const score = Number(data.risk_score || 0);
  
  // Format SHAP / Attribution data
  const shapList = data.shap_values || [];
  const shapData = shapList.map(item => ({
    feature: item.feature,
    value: Number(item.contribution || 0),
    rawValue: item.value
  })).slice(0, 8);

  const flags = data.flags || [];
  const negativeSpace = data.negative_space_findings || data.negative_space || [];
  const peerContext = data.peer_context || [];

  return (
    <div className="pb-12">
      {/* Header Strip */}
      <div className="bg-slate-950 border-b border-slate-800 p-6 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-4">
          <div>
            <div className="flex items-center gap-4 mb-1">
              <h1 className="text-4xl font-bold font-mono text-white">{cseId}</h1>
              <span className="bg-slate-800 text-slate-300 px-3 py-1 rounded-md text-sm border border-slate-700 font-semibold">
                Sector: {data.sector || 'Unknown'}
              </span>
            </div>
            <p className="text-slate-500 text-xs font-mono">Submission Batch: {batchId}</p>
          </div>
          
          <div className="flex items-center gap-6 text-right">
            <div>
              <p className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-bold">Risk Assessment</p>
              <RiskBadge level={data.risk_level} />
            </div>
            <div className="text-6xl font-black text-white tracking-tight">
              {score.toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        
        {/* Score Breakdown Card */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 text-slate-100">Risk Score Decomposition</h2>
          <ScoreBar breakdown={data.score_breakdown} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          
          {/* Left Column (60%) */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* SHAP Chart */}
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-sm">
              <h3 className="text-md font-semibold mb-1 text-slate-100">Key Risk Drivers (Feature Attribution)</h3>
              <p className="text-xs text-slate-400 mb-4">Positive contribution increases supervisory risk score; negative decreases risk.</p>
              <div className="h-64 w-full">
                {shapData.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-slate-500 text-sm">No attribution metrics available.</div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={shapData} layout="vertical" margin={{ left: 30, right: 20 }}>
                      <XAxis type="number" stroke="#94a3b8" />
                      <YAxis dataKey="feature" type="category" width={140} stroke="#94a3b8" tick={{fontSize: 11}} />
                      <Tooltip 
                        cursor={{fill: '#334155', opacity: 0.4}} 
                        contentStyle={{backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px'}}
                        formatter={(val) => [`${Number(val).toFixed(2)} pts`, 'Risk Contribution']}
                      />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {shapData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#ef4444' : '#3b82f6'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Flags */}
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <h3 className="text-md font-semibold text-slate-100">Operational Flags & Rule Triggers</h3>
                <span className="bg-slate-700 px-2.5 py-0.5 rounded-full text-xs font-bold text-slate-200">
                  {flags.length}
                </span>
              </div>
              
              <div className="space-y-4">
                {flags.map((flag, idx) => {
                  const evidenceList = flag.evidence_ids || flag.evidence || [];
                  const isExecGap = flag.flag_type === 'execution_gap' || (flag.rule_id && !flag.rule_id.startsWith('R-05') && !flag.rule_id.startsWith('R-06') && !flag.rule_id.startsWith('R-07'));
                  return (
                    <div key={idx} className="bg-slate-900/70 p-4 rounded-lg border border-slate-700">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                          isExecGap ? 'bg-orange-500/20 text-orange-400 border-orange-500/50' : 'bg-purple-500/20 text-purple-400 border-purple-500/50'
                        }`}>
                          {isExecGap ? 'EXECUTION GAP' : 'NEGATIVE SPACE'}
                        </span>
                        <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-[10px] font-bold font-mono">
                          {flag.rule_id}
                        </span>
                        <span className="font-bold text-slate-100 text-sm">{flag.rule_name}</span>
                        <span className="ml-auto">
                          <RiskBadge level={flag.severity || 'HIGH'} />
                        </span>
                      </div>
                      <p className="text-sm text-slate-300 mb-3 leading-relaxed">{flag.description}</p>
                      {evidenceList.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Cited Evidence Records:</p>
                          <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
                            {evidenceList.map(ev => (
                              <span key={ev} className="bg-slate-950 text-slate-300 border border-slate-800 px-2 py-0.5 rounded text-xs font-mono">
                                {ev}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
                {flags.length === 0 && (
                  <p className="text-slate-500 text-sm py-4 text-center">No rule violations or execution gaps detected for this entity.</p>
                )}
              </div>
            </div>
            
          </div>

          {/* Right Column (40%) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Negative Space */}
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <h3 className="text-md font-semibold text-slate-100">Negative Space (Blind Spots)</h3>
                <span className="bg-purple-500/20 text-purple-400 border border-purple-500/50 px-2.5 py-0.5 rounded-full text-xs font-bold">
                  {negativeSpace.length}
                </span>
              </div>
              
              <div className="space-y-4">
                {negativeSpace.map((ns, idx) => (
                  <div key={idx} className="bg-slate-900/80 p-4 rounded-lg border border-slate-700/60 border-l-4 border-l-purple-500">
                    <div className="flex justify-between items-start mb-1.5">
                      <span className="text-[10px] font-bold uppercase text-purple-400 tracking-wider">
                        {ns.finding_type || ns.type}
                      </span>
                      <RiskBadge level={ns.severity || 'HIGH'} />
                    </div>
                    <p className="text-sm text-slate-200 mb-3 font-medium">{ns.description}</p>
                    <div className="bg-slate-950 p-2.5 rounded text-xs font-mono text-slate-300 mb-2 border border-slate-800 space-y-1">
                      <div><span className="text-slate-500">Expected:</span> <span className="text-emerald-400">{ns.expected}</span></div>
                      <div><span className="text-slate-500">Observed:</span> <span className="text-rose-400">{ns.observed}</span></div>
                    </div>
                  </div>
                ))}
                {negativeSpace.length === 0 && (
                  <p className="text-slate-500 text-sm py-4 text-center">No negative space or telemetry blind spots detected.</p>
                )}
              </div>
            </div>

            {/* Peer Comparison Panel */}
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-sm">
              <h3 className="text-md font-semibold mb-1 text-slate-100">Sector Peer Comparison</h3>
              <p className="text-xs text-slate-400 mb-4">Relative position against {data.sector || 'sector'} entities.</p>
              <div className="space-y-4">
                {peerContext.map((item) => {
                  const labelMap = {
                    escalation_rate: 'Escalation Rate',
                    mean_closure_time_critical: 'Mean Critical Closure Time (min)',
                    critical_asset_telemetry_ratio: 'Critical Asset Telemetry Ratio',
                    case_linkage_rate: 'Case Linkage Rate',
                    critical_fast_closure_rate: 'Fast Closure Rate (<8m)'
                  };
                  const label = labelMap[item.metric] || item.metric;
                  return (
                    <div key={item.metric} className="bg-slate-900/60 p-3 rounded-lg border border-slate-700/50">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-200 font-semibold">{label}</span>
                      </div>
                      <div className="flex justify-between text-xs text-slate-400 font-mono mb-2">
                        <span>CSE: <strong className="text-blue-400">{Number(item.cse_value || 0).toFixed(2)}</strong></span>
                        <span>Peer Mean: <strong className="text-slate-300">{Number(item.peer_mean || 0).toFixed(2)}</strong></span>
                      </div>
                      <div className="w-full bg-slate-950 h-2 rounded-full relative border border-slate-800 overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 rounded-full" 
                          style={{ width: `${Math.min(Math.max((Number(item.cse_value || 0) / Math.max(Number(item.peer_mean || 1) * 2, 0.01)) * 100, 5), 100)}%` }} 
                        />
                      </div>
                    </div>
                  );
                })}
                {peerContext.length === 0 && (
                  <p className="text-slate-500 text-sm py-4 text-center">No peer benchmark data available.</p>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Supervisor Note */}
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-md font-semibold text-slate-100">Supervisor Review Annotations</h3>
            {savedSuccess && <span className="text-xs text-green-400 font-semibold">Note saved successfully!</span>}
          </div>
          <textarea 
            value={noteInput}
            onChange={(e) => setNoteInput(e.target.value)}
            placeholder="Add internal supervisor findings, audit notes, or verification comments for this entity..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 min-h-[100px] mb-3 font-sans"
          />
          <div className="flex justify-end">
            <button 
              onClick={handleSaveNote}
              disabled={savingNote}
              className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-lg font-medium text-sm transition-colors disabled:opacity-50 shadow-sm"
            >
              {savingNote ? 'Saving...' : 'Save Supervisor Note'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
