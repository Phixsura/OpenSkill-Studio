"use client";

interface FeatureTogglesProps { toggles: Record<string, boolean>; total: number;
  enabled: number; onToggle: (feature: string) => void; }

export function FeatureTogglesPanel({ toggles, total, enabled, onToggle }: FeatureTogglesProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Feature Toggles</h3>
        <span className="text-xs text-gray-400">{enabled}/{total} enabled</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {Object.entries(toggles).map(([name, on]) => (
          <div key={name} className="flex items-center justify-between px-4 py-2.5">
            <code className="text-sm font-mono">{name}</code>
            <button onClick={() => onToggle(name)}
              className={`relative h-6 w-11 rounded-full transition ${on ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition ${on ? "left-[22px]" : "left-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
