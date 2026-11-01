"use client";

interface LogEntry { level: string; message: string; service: string; traceId: string; }
interface StructuredLogViewerProps { logs: LogEntry[]; total: number;
  byLevel: Record<string, number>; errorPct: number; }

const LEVEL_COLORS: Record<string, string> = {
  ERROR: "text-red-500", WARN: "text-yellow-500", INFO: "text-blue-400", DEBUG: "text-gray-500",
};

export function StructuredLogViewer({ logs, total, byLevel, errorPct }: StructuredLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Structured Logs</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{total} logs</span>
          {errorPct > 0 && <span className="text-red-500">{errorPct}% errors</span>}
        </div>
      </div>
      <div className="flex gap-2 px-4 py-1.5 border-b dark:border-gray-700 text-[10px]">
        {Object.entries(byLevel).map(([lv, c]) => (
          <span key={lv} className={LEVEL_COLORS[lv] ?? "text-gray-400"}>{lv}: {c}</span>
        ))}
      </div>
      <div className="bg-gray-950 text-gray-200 font-mono text-xs max-h-48 overflow-y-auto p-2">
        {logs.map((l, i) => (
          <div key={i} className="py-0.5">
            <span className={`${LEVEL_COLORS[l.level] ?? ""} mr-1`}>[{l.level}]</span>
            {l.service && <span className="text-gray-500 mr-1">{l.service}</span>}
            <span>{l.message}</span>
            {l.traceId && <span className="text-gray-600 ml-1">({l.traceId})</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
