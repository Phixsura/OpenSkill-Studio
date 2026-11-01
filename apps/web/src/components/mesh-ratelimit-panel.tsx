"use client";
interface MeshLimit { key: string; rpm: number; currentCount: number; }
interface MeshRatelimitPanelProps { limits: MeshLimit[]; }
export function MeshRatelimitPanel({ limits }: MeshRatelimitPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Mesh Rate Limits</h3>
        <span className="text-xs text-gray-400">{limits.length} limits</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {limits.map(l => (
          <div key={l.key} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{l.key}</span>
            <span className={`${l.currentCount >= l.rpm ? "text-red-500" : "text-gray-400"}`}>
              {l.currentCount}/{l.rpm} rpm
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
