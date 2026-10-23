"use client";

interface Flag { key: string; label: string; enabled: boolean; rolloutPct: number; environments: string[]; }
interface FeatureFlagPanelProps { flags: Flag[]; environment: string; enabled: number;
  total: number; onToggle: (key: string) => void; }

export function FeatureFlagPanel({ flags, environment, enabled, total, onToggle }: FeatureFlagPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚩 Feature Flags</h3>
        <div className="flex gap-2 text-xs">
          <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">{environment}</span>
          <span className="text-gray-400">{enabled}/{total} on</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {flags.map(f => (
          <div key={f.key} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="text-sm font-medium">{f.label}</div>
              <div className="text-xs text-gray-400 font-mono">{f.key} · {f.rolloutPct}% rollout</div>
            </div>
            <button onClick={() => onToggle(f.key)}
              className={`w-10 h-5 rounded-full transition ${f.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-4 h-4 rounded-full bg-white shadow transform transition ${f.enabled ? "translate-x-5" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
