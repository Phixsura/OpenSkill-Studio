"use client";
interface ShapeRule { source: string; destination: string; type: string; active: boolean; }
interface MeshShapePanelProps { rules: ShapeRule[]; activeCount: number; }
const TYPE_COLOR: Record<string, string> = { delay: "bg-yellow-100 text-yellow-700", abort: "bg-red-100 text-red-700", rate_limit: "bg-blue-100 text-blue-700" };
export function MeshShapePanel({ rules, activeCount }: MeshShapePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌊 Traffic Shaping</h3>
        <span className={`text-xs ${activeCount > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {activeCount > 0 ? `${activeCount} active rules` : "No shaping"} · {rules.length} total
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map((r, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.source} → {r.destination}</span>
            <span className={`px-1 rounded text-[10px] ${TYPE_COLOR[r.type] ?? "bg-gray-100"}`}>{r.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
