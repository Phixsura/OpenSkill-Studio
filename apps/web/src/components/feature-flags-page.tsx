"use client";

interface Flag { key: string; description: string; enabled: boolean;
  rolloutPct: number; environment: string; createdBy: string; }
interface FeatureFlagsPageProps { flags: Flag[]; enabled: number; disabled: number;
  onToggle: (key: string) => void; onCreate: () => void; }

export function FeatureFlagsPage({ flags, enabled, disabled, onToggle, onCreate }: FeatureFlagsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚩 Feature Flags</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{enabled} on · {disabled} off</span>
          <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ New Flag</button>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {flags.map(f => (
          <div key={f.key} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono font-medium">{f.key}</code>
                <span className="text-xs text-gray-400">{f.rolloutPct}%</span>
                <span className="text-xs text-gray-400 capitalize">{f.environment}</span>
              </div>
              {f.description && <p className="text-xs text-gray-400 mt-0.5">{f.description}</p>}
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
