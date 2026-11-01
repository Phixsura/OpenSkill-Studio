"use client";

interface HistoryEntry { method: string; path: string; status: number; durationMs: number; }
interface PlaygroundConsoleProps { sessionId: string; history: HistoryEntry[];
  variables: Record<string, string>; onSend: (method: string, path: string) => void; }

const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600",
};

export function PlaygroundConsole({ sessionId, history, variables, onSend }: PlaygroundConsoleProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-3 bg-gray-900 text-white">
        <span className="text-xs font-mono">API Playground · {sessionId.slice(0, 12)}</span>
        <span className="text-xs text-gray-400">{history.length} requests</span>
      </div>
      <div className="bg-gray-950 p-3 max-h-48 overflow-y-auto font-mono text-xs space-y-1">
        {history.map((h, i) => (
          <div key={i} className="flex gap-2">
            <span className={`w-10 font-bold ${METHOD_COLOR[h.method] || ""}`}>{h.method}</span>
            <span className={h.status < 400 ? "text-green-400" : "text-red-400"}>{h.status}</span>
            <span className="text-gray-400 flex-1">{h.path}</span>
            <span className="text-gray-500">{h.durationMs}ms</span>
          </div>
        ))}
      </div>
      {Object.keys(variables).length > 0 && (
        <div className="bg-gray-900 px-3 py-1.5 text-xs text-gray-400">
          Vars: {Object.entries(variables).map(([k, v]) => `${k}=${v}`).join(", ")}
        </div>
      )}
    </div>
  );
}
