"use client";
interface DepChange { service: string; added: string[]; removed: string[]; risk: string; }
interface DepChangeTrackPanelProps { changes: DepChange[]; totalAdded: number; totalRemoved: number; hasRemovals: boolean; }
export function DepChangeTrackPanel({ changes, totalAdded, totalRemoved, hasRemovals }: DepChangeTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Dependency Changes</h3>
        <span className={`text-xs ${hasRemovals ? "text-yellow-600" : "text-green-600"}`}>
          +{totalAdded} added · -{totalRemoved} removed · {changes.length} services
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {changes.map(c => (
          <div key={c.service} className="px-4 py-1.5 text-xs">
            <span className="font-mono font-semibold">{c.service}: </span>
            {c.added.map(a => <span key={a} className="text-green-600 mr-1">+{a}</span>)}
            {c.removed.map(r => <span key={r} className="text-red-500 mr-1">-{r}</span>)}
          </div>
        ))}
      </div>
    </div>
  );
}
