"use client";

interface MockResp { path: string; method: string; status: number; delayMs: number; }
interface MockRespBuilderProps { mocks: MockResp[]; total: number;
  byMethod: Record<string, number>; onAdd: () => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500",
};

export function MockRespBuilder({ mocks, total, byMethod, onAdd }: MockRespBuilderProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎭 Mock Responses</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{total} mocks</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {mocks.map((m, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 text-[10px] text-white rounded ${METHOD_COLORS[m.method] ?? "bg-gray-500"}`}>{m.method}</span>
              <span className="font-mono">{m.path}</span>
            </div>
            <span className="text-gray-400">{m.status}{m.delayMs > 0 ? ` · ${m.delayMs}ms` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
