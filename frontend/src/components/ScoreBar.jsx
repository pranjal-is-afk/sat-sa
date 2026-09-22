export default function ScoreBar({ breakdown }) {
  if (!breakdown) return null;
  
  const { rules = 0, statistical = 0, peer = 0, negative_space = 0 } = breakdown;
  const total = rules + statistical + peer + negative_space || 1;
  
  const rulesPct = (rules / total) * 100;
  const statPct = (statistical / total) * 100;
  const peerPct = (peer / total) * 100;
  const nsPct = (negative_space / total) * 100;
  
  return (
    <div className="w-full">
      <div className="h-4 w-full bg-slate-700 rounded-full overflow-hidden flex">
        {rulesPct > 0 && <div style={{ width: `${rulesPct}%` }} className="bg-red-500 h-full" title={`Rules: ${rules}`} />}
        {statPct > 0 && <div style={{ width: `${statPct}%` }} className="bg-orange-500 h-full" title={`Statistical: ${statistical}`} />}
        {peerPct > 0 && <div style={{ width: `${peerPct}%` }} className="bg-yellow-500 h-full" title={`Peer: ${peer}`} />}
        {nsPct > 0 && <div style={{ width: `${nsPct}%` }} className="bg-purple-500 h-full" title={`Negative Space: ${negative_space}`} />}
      </div>
      <div className="flex gap-4 mt-2 text-xs text-slate-400 justify-center">
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Rules</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500"></span> Statistical</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Peer</div>
        <div className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500"></span> Negative Space</div>
      </div>
    </div>
  );
}
