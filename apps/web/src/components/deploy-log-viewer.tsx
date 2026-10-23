"use client";

interface LogEntry { level: string; message: string; seq: number; }
interface DeployLogViewerProps { deployId: string; logs: LogEntry[];
  total: number; errorCount: number; }

const LEVEL_COLORS: Record<string, string> = {
  info: "text-blue-500", warn: "text-yellow-500", error: "text-red-500",
  debug: "text-gray-400", success: "text-green-500",
};

export function DeployLogViewer({ deployId, logs, total, errorCount }: DeployLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">📋 Deploy Logs</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400 font-mono">{deployId}</span>
          <span className="text-gray-400">{total} lines</span>
          {errorCount > 0 && <span className="text-red-500">{errorCount} errors</span>}
        </div>
      </div>
      <div className="bg-gray-900 text-gray-200 p-3 max-h-64 overflow-y-auto font-mono text-xs">
        {logs.map(l => (
          <div key={l.seq} className="py-0.5">
            <span className="text-gray-500 mr-2">{l.seq}</span>
            <span className={`mr-2 uppercase ${LEVEL_COLORS[l.level] ?? ""}`}>[{l.level}]</span>
            <span>{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
