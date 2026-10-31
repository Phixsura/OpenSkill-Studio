"use client";
interface Endpoint { method: string; path: string; service: string; deprecated: boolean; }
interface EpInventoryPanelProps { endpoints: Endpoint[]; total: number; deprecated: number; services: number; }
const METHOD_COLOR: Record<string, string> = { GET: "text-green-600", POST: "text-blue-500", PUT: "text-yellow-600", DELETE: "text-red-500" };
export function EpInventoryPanel({ endpoints, total, deprecated, services }: EpInventoryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Endpoint Inventory</h3>
        <span className="text-xs text-gray-400">{total} endpoints · {services} services · {deprecated} deprecated</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map((e, i) => (
          <div key={i} className={`flex justify-between px-4 py-1.5 text-xs ${e.deprecated ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`font-bold w-12 ${METHOD_COLOR[e.method] ?? ""}`}>{e.method}</span>
              <span className={`font-mono ${e.deprecated ? "line-through" : ""}`}>{e.path}</span>
            </div>
            <span className="text-gray-400">{e.service}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
