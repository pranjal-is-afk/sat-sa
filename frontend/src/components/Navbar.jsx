import { NavLink } from 'react-router-dom';

export default function Navbar({ batchId }) {
  return (
    <nav className="bg-slate-950 border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <div className="font-bold text-white text-xl">SAT-SA</div>
        <div className="text-slate-400 text-sm">Supervisory Analytics</div>
      </div>
      
      {batchId && (
        <div className="flex gap-6">
          <NavLink 
            to="/overview" 
            className={({isActive}) => `text-sm font-medium pb-1 ${isActive ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-300 hover:text-white'}`}
          >
            Overview
          </NavLink>
          <NavLink 
            to="/ranking" 
            className={({isActive}) => `text-sm font-medium pb-1 ${isActive ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-300 hover:text-white'}`}
          >
            Risk Ranking
          </NavLink>
          <NavLink 
            to="/negative-space" 
            className={({isActive}) => `text-sm font-medium pb-1 ${isActive ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-300 hover:text-white'}`}
          >
            Negative Space
          </NavLink>
        </div>
      )}

      <div>
        {batchId ? (
          <span className="bg-blue-900/50 text-blue-400 border border-blue-800 px-3 py-1 rounded text-xs font-mono">
            Batch: {batchId.slice(0, 8)}...
          </span>
        ) : (
          <span className="text-slate-500 text-sm">No active batch</span>
        )}
      </div>
    </nav>
  );
}
