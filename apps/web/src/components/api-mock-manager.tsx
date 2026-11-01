"use client";

interface Mock { method: string; path: string; status: number; hitCount: number; delayMs: number; }
interface ApiMockManagerProps { mocks: Mock[]; totalHits: number;
  onAdd: () => void; onClear: () => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-orange-600",
};

export function ApiMockManager({ mocks, totalHits, onAdd, onClear }: ApiMockManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎭 API Mocks</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{mocks.length} mocks · {totalHits} hits</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
          <button onClick={onClear} className="text-xs text-red-500">Clear</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {mocks.map(m => (
          <div key={`${m.method}:${m.path}`} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2 text-sm">
              <span className={`font-mono font-bold text-xs ${METHOD_COLORS[m.method] ?? ""}`}>{m.method}</span>
              <span className="font-mono text-gray-600 dark:text-gray-300">{m.path}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{m.status}</span>
              <span>{m.hitCount} hits</span>
              {m.delayMs > 0 && <span>{m.delayMs}ms delay</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
