"use client";

interface MockEndpoint { method: string; path: string; hits: number; }
interface MockServerConfigProps { mocks: MockEndpoint[]; totalHits: number;
  onAdd: (method: string, path: string) => void; }

const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-orange-600",
};

export function MockServerConfig({ mocks, totalHits, onAdd }: MockServerConfigProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🎭 Mock Server</h3>
        <span className="text-xs text-gray-400">{totalHits} total hits</span>
      </div>
      <div className="space-y-2 mb-4">
        {mocks.map((m, i) => (
          <div key={i} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span className={`font-bold text-xs w-14 ${METHOD_COLOR[m.method] || ""}`}>{m.method}</span>
              <span className="font-mono text-xs">{m.path}</span>
            </div>
            <span className="text-xs text-gray-400">{m.hits} hits</span>
          </div>
        ))}
      </div>
      <button onClick={() => onAdd("GET", "/api/new")}
        className="w-full py-2 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-400 hover:text-gray-600 hover:border-gray-400">
        + Add Mock Endpoint
      </button>
    </div>
  );
}
