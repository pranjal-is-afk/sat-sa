export default function MetricCard({ title, value, subtitle, icon: Icon, color = 'blue' }) {
  const colors = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    orange: 'text-orange-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
    slate: 'text-slate-400'
  };
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div className="flex items-center justify-between mb-2">
        <p className="text-slate-400 text-sm">{title}</p>
        {Icon && <Icon className={`w-5 h-5 ${colors[color]}`} />}
      </div>
      <p className={`text-3xl font-bold ${colors[color]}`}>{value}</p>
      {subtitle && <p className="text-slate-500 text-xs mt-1">{subtitle}</p>}
    </div>
  );
}
