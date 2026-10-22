"use client";

interface SandboxLogViewerProps {
  logs: Array<{ level: string; message: string }>;
  maxHeight?: number;
}

const LEVEL_COLORS: Record<string, string> = {
  info: "text-blue-600",
  warn: "text-yellow-600",
  error: "text-red-600",
  debug: "text-gray-400",
  stderr: "text-orange-500",
};

export function SandboxLogViewer({ logs, maxHeight = 300 }: SandboxLogViewerProps) {
  if (logs.length === 0) {
    return <p className="py-4 text-center text-sm text-gray-400">No logs</p>;
  }

  return (
    <div
      className="overflow-auto rounded-lg bg-gray-900 p-3 font-mono text-xs text-gray-100"
      style={{ maxHeight: `${maxHeight}px` }}
    >
      {logs.map((log, i) => (
        <div key={i} className="flex gap-2">
          <span className={`shrink-0 font-bold ${LEVEL_COLORS[log.level] ?? "text-gray-400"}`}>
            [{log.level.toUpperCase().padEnd(5)}]
          </span>
          <span className="break-all">{log.message}</span>
        </div>
      ))}
    </div>
  );
}
