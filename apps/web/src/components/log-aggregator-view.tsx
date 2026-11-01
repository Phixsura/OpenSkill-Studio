"use client";

interface LogEntry { source: string; level: string; message: string; timestamp: string; }
interface LogAggregatorViewProps { logs: LogEntry[]; totalLogs: number;
  bySource: Record<string, number>; byLevel: Record<string, number>; hasErrors: boolean; }

const levelColor: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-500", warning: "text-yellow-500",
  error: "text-red-500", critical: "text-red-700",
};

export function LogAggregatorView({ logs, totalLogs, bySource, byLevel, hasErrors }: LogAggregatorViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Aggregated Logs</h2>
        <div className="flex items-center gap-2">
          {hasErrors && <span className="text-xs text-red-500">⚠️ Errors detected</span>}
          <span className="text-xs text-gray-400">{totalLogs} total</span>
        </div>
      </div>
      <div className="flex gap-2">
        {Object.entries(bySource).map(([s, c]) => (
          <span key={s} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{s}: {c}</span>
        ))}
      </div>
      <div className="max-h-60 overflow-y-auto rounded border bg-gray-900 p-2 dark:border-gray-700">
        {logs.slice(0, 50).map((l, i) => (
          <div key={i} className="flex gap-2 py-0.5 font-mono text-xs">
            <span className="w-16 text-gray-500">{l.timestamp.slice(11, 19)}</span>
            <span className="w-12 rounded bg-gray-800 px-1 text-center text-[10px]">{l.source}</span>
            <span className={`w-14 uppercase ${levelColor[l.level] ?? ""}`}>{l.level}</span>
            <span className="text-gray-200">{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
