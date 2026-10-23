"use client";

interface LogEntry { level: string; service: string; message: string; timestamp?: string; }
interface StructuredLogViewerProps { logs: LogEntry[]; total: number;
  byLevel: Record<string, number>; hasErrors: boolean; }

const LVL: Record<string, string> = {
  error: "text-red-600 bg-red-50 dark:bg-red-900/20",
  warn: "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20",
  info: "text-blue-600 bg-blue-50 dark:bg-blue-900/20",
  debug: "text-gray-500 bg-gray-50 dark:bg-gray-800",
};

export function StructuredLogViewer({ logs, total, byLevel, hasErrors }: StructuredLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Logs</h3>
        <div className="flex gap-2 text-xs">
          {Object.entries(byLevel).map(([k, v]) => (
            <span key={k} className={`px-1.5 py-0.5 rounded ${LVL[k] || ""}`}>{k}: {v}</span>
          ))}
        </div>
      </div>
      <div className="max-h-72 overflow-y-auto font-mono text-xs">
        {logs.map((l, i) => (
          <div key={i} className={`flex gap-2 px-4 py-1 border-b last:border-0 dark:border-gray-800 ${l.level === "error" ? "bg-red-50/50 dark:bg-red-900/5" : ""}`}>
            <span className={`px-1 rounded font-bold uppercase w-12 text-center ${LVL[l.level] || ""}`}>{l.level}</span>
            <span className="text-gray-400 w-16 shrink-0">{l.service}</span>
            <span className="truncate">{l.message}</span>
          </div>
        ))}
      </div>
      <div className="px-4 py-2 text-xs text-gray-400 border-t dark:border-gray-700">{total} total entries</div>
    </div>
  );
}
