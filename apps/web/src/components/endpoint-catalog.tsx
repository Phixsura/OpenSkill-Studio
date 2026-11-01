"use client";

interface Endpoint { method: string; path: string; description: string; auth: boolean; category: string; }
interface EndpointCatalogProps { endpoints: Endpoint[]; categories: { category: string; count: number }[]; }

const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-orange-600",
};

export function EndpointCatalog({ endpoints, categories }: EndpointCatalogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 API Endpoints</h3>
        <div className="flex gap-2 mt-1">
          {categories.map(c => (
            <span key={c.category} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded capitalize">{c.category} ({c.count})</span>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={`${e.method}-${e.path}`} className="flex items-center justify-between px-4 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span className={`font-bold text-xs w-14 ${METHOD_COLOR[e.method] || ""}`}>{e.method}</span>
              <span className="font-mono text-xs">{e.path}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>{e.description}</span>
              {e.auth && <span>🔒</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
