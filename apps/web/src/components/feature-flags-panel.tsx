"use client";

interface Flag { key: string; description: string; enabled: boolean; rollout_pct: number; }
interface FeatureFlagsPanelProps { flags: Flag[]; onToggle: (key: string, enabled: boolean) => void; }

export function FeatureFlagsPanel({ flags, onToggle }: FeatureFlagsPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Feature Flags</h3>
      {flags.length === 0 ? <p className="mt-2 text-sm text-gray-400">No feature flags configured.</p> : (
        <ul className="mt-3 space-y-2">
          {flags.map(f => (
            <li key={f.key} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{f.key}</p>
                <p className="text-xs text-gray-400">{f.description} · {f.rollout_pct}% rollout</p>
              </div>
              <button onClick={() => onToggle(f.key, !f.enabled)}
                className={`relative h-6 w-11 rounded-full transition ${f.enabled ? "bg-green-500" : "bg-gray-300"}`}>
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${f.enabled ? "translate-x-5" : "translate-x-0.5"}`} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
