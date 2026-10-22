"use client";

interface HistoryEntry { request: { method?: string; path?: string }; response: { status?: number }; timestamp: string; }
interface PlaygroundHistoryProps { history: HistoryEntry[]; onReplay: (index: number) => void; }

export function PlaygroundHistory({ history, onReplay }: PlaygroundHistoryProps) {
  if (history.length === 0) return <p className="text-sm text-gray-400">No request history.</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700"><h3 className="text-sm font-semibold">History</h3></div>
      <ul className="max-h-48 overflow-y-auto">
        {history.map((h, i) => (
          <li key={i} className="flex items-center justify-between border-b px-3 py-2 text-xs dark:border-gray-700">
            <span className="flex items-center gap-2">
              <span className="font-mono font-bold">{h.request.method || "GET"}</span>
              <span className="truncate max-w-[150px]">{h.request.path || "/"}</span>
            </span>
            <span className="flex items-center gap-2">
              <span className={h.response.status && h.response.status < 400 ? "text-green-600" : "text-red-600"}>{h.response.status}</span>
              <button onClick={() => onReplay(i)} className="text-blue-600">↻</button>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
