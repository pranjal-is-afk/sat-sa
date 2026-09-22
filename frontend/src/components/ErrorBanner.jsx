import { X } from 'lucide-react';

export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  
  return (
    <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg flex items-center justify-between mb-6">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-red-400">Error:</span>
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-400 hover:text-red-300">
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
