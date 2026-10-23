"use client";

interface FlagInfo { key: string; dflt: boolean; rolloutPct: number;
  targetedUsers: number; targetedOrgs: number; }
interface FeatureFlagPanelProps { flags: FlagInfo[]; onToggle: (key: string) => void; }

export function FeatureFlagPanel({ flags, onToggle }: FeatureFlagPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🚩 Feature Flags</h3>
      <div className="space-y-2">
        {flags.map(f => (
          <div key={f.key} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div>
              <span className="text-sm font-mono">{f.key}</span>
              <div className="flex gap-2 text-xs text-gray-400 mt-0.5">
                {f.rolloutPct > 0 && <span>{f.rolloutPct}% rollout</span>}
                {f.targetedUsers > 0 && <span>{f.targetedUsers} users</span>}
                {f.targetedOrgs > 0 && <span>{f.targetedOrgs} orgs</span>}
              </div>
            </div>
            <button onClick={() => onToggle(f.key)}
              className={`w-9 h-5 rounded-full ${f.dflt ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-4 h-4 rounded-full bg-white transform ${f.dflt ? "translate-x-4" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
