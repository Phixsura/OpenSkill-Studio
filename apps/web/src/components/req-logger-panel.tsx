"use client";
interface LogEntry { method: string; path: string; status: number; durationMs: number; }
interface ReqLoggerPanelProps { logs: LogEntry[]; total: number; byStatus: Record<string, number>; }
export function ReqLoggerPanel({ logs, total, byStatus }: ReqLoggerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Request Log</h3>
        <div className="flex gap-2 text-xs text-gray-400">
          {Object.entries(byStatus).map(([k, v]) => <span key={k}>{k}: {v}</span>)}
          <span>· {total} total</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {logs.map((l, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold w-10">{l.method}</span>
              <span className="font-mono">{l.path}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={l.status >= 400 ? "text-red-500" : "text-green-600"}>{l.status}</span>
              <span className="text-gray-400">{l.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
