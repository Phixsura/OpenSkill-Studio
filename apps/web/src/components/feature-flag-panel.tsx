"use client";

interface Flag { flagId: string; name: string; description: string; enabled: boolean; rolloutPct: number; }

export function FeatureFlagPanel({ flags, onToggle, onRollout }: {
  flags: Flag[]; onToggle?: (flagId: string, enabled: boolean) => void; onRollout?: (flagId: string, pct: number) => void;
}) {
  if (!flags.length) return <div className="text-center text-gray-400 py-6 text-sm">No feature flags</div>;
  return (
    <div className="space-y-2">
      {flags.map(f => (
        <div key={f.flagId} className="border dark:border-gray-700 rounded-xl p-3 flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${f.enabled ? "bg-green-500" : "bg-gray-300"}`} />
              <span className="font-medium text-sm">{f.name}</span>
              {f.rolloutPct > 0 && f.rolloutPct < 100 && <span className="text-xs bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded">{f.rolloutPct}%</span>}
            </div>
            {f.description && <span className="text-xs text-gray-500 ml-5">{f.description}</span>}
          </div>
          <button onClick={() => onToggle?.(f.flagId, !f.enabled)}
            className={`text-xs px-3 py-1 rounded-lg ${f.enabled ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"}`}>
            {f.enabled ? "Disable" : "Enable"}
          </button>
        </div>
      ))}
    </div>
  );
}
