"use client";
interface VersionNegPanelProps { active: string[]; deprecated: string[]; latest: string; }
export function VersionNegPanel({ active, deprecated, latest }: VersionNegPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 API Versions</h3>
        <span className="text-xs text-gray-400">latest: {latest} · {active.length} active · {deprecated.length} deprecated</span>
      </div>
      <div className="p-4 flex gap-2 flex-wrap">
        {active.map(v => <span key={v} className="px-2 py-0.5 rounded bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs">{v}</span>)}
        {deprecated.map(v => <span key={v} className="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-500 text-xs line-through">{v}</span>)}
      </div>
    </div>
  );
}
