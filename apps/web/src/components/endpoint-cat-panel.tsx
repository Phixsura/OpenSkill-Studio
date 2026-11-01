"use client";
interface Endpoint { method: string; path: string; service: string; authRequired: boolean; rateLimit: number; }
interface EndpointCatPanelProps { endpoints: Endpoint[]; total: number; services: number; }
const METHOD_COLOR: Record<string, string> = { GET: "text-green-600", POST: "text-blue-500", PUT: "text-yellow-600", DELETE: "text-red-500" };
export function EndpointCatPanel({ endpoints, total, services }: EndpointCatPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 API Catalog</h3>
        <span className="text-xs text-gray-400">{total} endpoints · {services} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`font-bold w-12 ${METHOD_COLOR[e.method] ?? ""}`}>{e.method}</span>
              <span className="font-mono">{e.path}</span>
            </div>
            <span className="text-gray-400">{e.service}{e.authRequired ? " · 🔒" : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
