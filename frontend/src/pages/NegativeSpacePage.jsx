import { useState, useEffect, useMemo } from 'react';
import { getNegativeSpace } from '../api';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { EyeOff } from 'lucide-react';

export default function NegativeSpacePage({ batchId }) {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await getNegativeSpace(batchId);
        setFindings(res.data.findings || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch negative space findings');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [batchId]);

  const grouped = useMemo(() => {
    const groups = {
      MISSING_TELEMETRY: [],
      MISSING_ALERT_CATEGORY: [],
      MISSING_ESCALATION: []
    };
    
    findings.forEach(f => {
      if (groups[f.finding_type]) {
        groups[f.finding_type].push(f);
      } else {
        groups[f.finding_type] = [f];
      }
    });
    
    return groups;
  }, [findings]);

  if (loading) return <LoadingSpinner message="Scanning for blind spots..." />;

  const FindingCard = ({ finding }) => (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-3">
          <span className="font-mono text-blue-400 font-bold">{finding.cse_id}</span>
          {finding.asset_id && (
            <span className="bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-xs font-mono">
              Asset: {finding.asset_id}
            </span>
          )}
        </div>
        <RiskBadge level={finding.severity || 'MEDIUM'} />
      </div>
      
      <p className="text-slate-200 mb-4">{finding.description}</p>
      
      <div className="grid grid-cols-2 gap-4 bg-slate-900/80 p-3 rounded-lg border border-slate-800 text-sm font-mono mb-3">
        <div>
          <span className="text-slate-500 text-xs block mb-1">Expected</span>
          <span className="text-green-400">{finding.expected}</span>
        </div>
        <div>
          <span className="text-slate-500 text-xs block mb-1">Observed</span>
          <span className="text-red-400">{finding.observed}</span>
        </div>
      </div>
      
      {finding.peer_context && (
        <p className="text-xs text-slate-400 bg-slate-800/50 p-2 rounded italic border border-slate-700/30">
          Peer context: {finding.peer_context}
        </p>
      )}
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto pb-12">
      <div className="flex items-center gap-4 mb-2">
        <EyeOff className="w-8 h-8 text-slate-400" />
        <h1 className="text-3xl font-bold">Negative Space Findings</h1>
        <span className="bg-purple-500/20 text-purple-400 border border-purple-500/50 px-3 py-1 rounded-full text-sm font-bold">
          {findings.length} Total
        </span>
      </div>
      <p className="text-slate-400 mb-8">
        Detected absences in CSE security data — findings represent monitoring blind spots, not confirmed incidents.
      </p>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="space-y-10">
        
        {/* Missing Telemetry */}
        <section>
          <div className="border-b-2 border-purple-500/50 pb-2 mb-4">
            <h2 className="text-xl font-bold text-purple-400">Missing Telemetry</h2>
          </div>
          {grouped.MISSING_TELEMETRY?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {grouped.MISSING_TELEMETRY.map((f, i) => <FindingCard key={i} finding={f} />)}
            </div>
          ) : (
            <p className="text-slate-500 italic">No findings of this type.</p>
          )}
        </section>

        {/* Missing Alert Categories */}
        <section>
          <div className="border-b-2 border-red-500/50 pb-2 mb-4">
            <h2 className="text-xl font-bold text-red-400">Missing Alert Categories</h2>
          </div>
          {grouped.MISSING_ALERT_CATEGORY?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {grouped.MISSING_ALERT_CATEGORY.map((f, i) => <FindingCard key={i} finding={f} />)}
            </div>
          ) : (
            <p className="text-slate-500 italic">No findings of this type.</p>
          )}
        </section>

        {/* Missing Escalation */}
        <section>
          <div className="border-b-2 border-orange-500/50 pb-2 mb-4">
            <h2 className="text-xl font-bold text-orange-400">Missing Escalation Records</h2>
          </div>
          {grouped.MISSING_ESCALATION?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {grouped.MISSING_ESCALATION.map((f, i) => <FindingCard key={i} finding={f} />)}
            </div>
          ) : (
            <p className="text-slate-500 italic">No findings of this type.</p>
          )}
        </section>

      </div>
    </div>
  );
}
