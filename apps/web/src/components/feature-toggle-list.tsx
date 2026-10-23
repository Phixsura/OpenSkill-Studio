"use client";

interface Toggle { key: string; enabled: boolean; rolloutPct: number; segments: string[]; }
interface FeatureToggleListProps { toggles: Toggle[]; onToggle: (key: string) => void; }

export function FeatureToggleList({ toggles, onToggle }: FeatureToggleListProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🎚️ Feature Toggles</h3>
      <div className="space-y-2">
        {toggles.map(t => (
          <div key={t.key} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <span className="text-sm font-mono font-medium">{t.key}</span>
              <div className="flex gap-2 mt-0.5 text-xs text-gray-400">
                <span>{t.rolloutPct}% rollout</span>
                {t.segments.length > 0 && <span>Segments: {t.segments.join(", ")}</span>}
              </div>
            </div>
            <button onClick={() => onToggle(t.key)}
              className={`w-10 h-5 rounded-full transition ${t.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-4 h-4 rounded-full bg-white transition transform ${t.enabled ? "translate-x-5" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
