"use client";

interface Feature { name: string; enabled: boolean; description: string; owner: string; tags: string[]; }
interface FeatureRegPanelProps { features: Feature[]; enabled: number; total: number; }

export function FeatureRegPanel({ features, enabled, total }: FeatureRegPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚩 Feature Registry</h3>
        <span className="text-xs text-gray-400">{enabled}/{total} enabled</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {features.map(f => (
          <div key={f.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{f.name}</span>
              {f.description && <span className="text-gray-400 ml-2">{f.description}</span>}
            </div>
            <div className="flex items-center gap-2">
              {f.tags.map(t => <span key={t} className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{t}</span>)}
              <span className={`w-2 h-2 rounded-full ${f.enabled ? "bg-green-500" : "bg-gray-400"}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
