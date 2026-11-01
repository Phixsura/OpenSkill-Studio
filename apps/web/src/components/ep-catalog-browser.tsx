"use client";

interface Endpoint { path: string; method: string; tag: string; description: string; }
interface EpCatalogBrowserProps { endpoints: Endpoint[]; total: number;
  tags: string[]; byMethod: Record<string, number>; onSearch: (q: string) => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500", PATCH: "bg-orange-500",
};

export function EpCatalogBrowser({ endpoints, total, tags, byMethod, onSearch }: EpCatalogBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 API Catalog</h3>
        <span className="text-xs text-gray-400">{total} endpoints · {tags.length} tags</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 text-[10px] text-white rounded ${METHOD_COLORS[ep.method] ?? "bg-gray-500"}`}>{ep.method}</span>
              <span className="font-mono">{ep.path}</span>
            </div>
            <span className="text-gray-400">{ep.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
