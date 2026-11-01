"use client";

interface CapturedRequest { id: string; method: string; path: string; }
interface RequestReplayPanelProps { captures: CapturedRequest[];
  onReplay: (id: string) => void; onClear: () => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  PATCH: "text-orange-600", DELETE: "text-red-600",
};

export function RequestReplayPanel({ captures, onReplay, onClear }: RequestReplayPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔁 Request Replay</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{captures.length} captured</span>
          <button onClick={onClear} className="text-xs text-red-500 hover:underline">Clear</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {captures.map(c => (
          <div key={c.id} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2 text-sm">
              <span className={`font-mono font-bold text-xs ${METHOD_COLORS[c.method] ?? ""}`}>{c.method}</span>
              <span className="font-mono text-gray-600 dark:text-gray-300 truncate max-w-[200px]">{c.path}</span>
            </div>
            <button onClick={() => onReplay(c.id)} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">▶ Replay</button>
          </div>
        ))}
        {captures.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No captured requests</div>}
      </div>
    </div>
  );
}
