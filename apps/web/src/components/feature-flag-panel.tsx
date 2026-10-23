"use client";

interface Flag { key: string; enabled: boolean; percentage: number; description: string; }
interface FeatureFlagPanelProps { flags: Flag[]; onToggle: (key: string) => void; }

export function FeatureFlagPanel({ flags, onToggle }: FeatureFlagPanelProps) {
  const active = flags.filter(f => f.enabled).length;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Feature Flags</h3>
        <span className="text-xs text-gray-400">{active}/{flags.length} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {flags.map(f => (
          <div key={f.key} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium font-mono">{f.key}</p>
              {f.description && <p className="text-xs text-gray-500">{f.description}</p>}
              <span className="text-xs text-gray-400">{f.percentage}% rollout</span>
            </div>
            <button onClick={() => onToggle(f.key)}
              className={`relative h-6 w-11 rounded-full transition ${f.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition ${f.enabled ? "left-[22px]" : "left-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
