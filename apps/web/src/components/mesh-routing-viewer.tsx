"use client";

interface RouteRule { name: string; destination: string; conditions: { field: string; op: string; value: string }[]; }
interface WeightedDest { destination: string; pct: number; }
interface MeshRoutingViewerProps { rules: RouteRule[]; splits?: WeightedDest[]; }

export function MeshRoutingViewer({ rules, splits }: MeshRoutingViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Routing</h3>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map(r => (
          <div key={r.name} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-semibold">{r.name}</span>
              <span className="font-mono text-blue-500">{r.destination}</span>
            </div>
            {r.conditions.map((c, i) => (
              <span key={i} className="text-gray-400 mr-2">{c.field} {c.op} {c.value}</span>
            ))}
          </div>
        ))}
      </div>
      {splits && splits.length > 0 && (
        <div className="border-t dark:border-gray-700 p-4">
          <div className="text-xs text-gray-400 mb-2">Traffic Split</div>
          <div className="flex h-3 rounded-full overflow-hidden">
            {splits.map(s => (
              <div key={s.destination} className="bg-blue-500 first:bg-green-500" style={{ width: `${s.pct}%` }}
                title={`${s.destination}: ${s.pct}%`} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
