"use client";

interface PlaygroundExecInfo {
  execution_id: string;
  method: string;
  path: string;
  status_code: number;
  duration_ms: number;
  saved: boolean;
  name: string;
  timestamp: string;
}

interface PlaygroundRunnerCardProps {
  executions: PlaygroundExecInfo[];
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
  PATCH: "text-orange-700 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3_600_000)}h ago`;
}

export default function PlaygroundRunnerCard({ executions, appName }: PlaygroundRunnerCardProps) {
  const savedCount = executions.filter((e) => e.saved).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Playground</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          {savedCount > 0 && <span className="text-xs text-gray-400">⭐ {savedCount} saved</span>}
          <span className="text-xs text-gray-400">{executions.length} requests</span>
        </div>
      </div>

      {executions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No requests yet</p>
      ) : (
        <div className="space-y-1.5">
          {executions.map((e) => (
            <div
              key={e.execution_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${METHOD_COLORS[e.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {e.method}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{e.path}</span>
                {e.saved && <span className="text-[10px]">⭐</span>}
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                <span
                  className={
                    e.status_code >= 400 ? "text-red-500" : "text-green-600 dark:text-green-400"
                  }
                >
                  {e.status_code}
                </span>
                <span>{e.duration_ms.toFixed(0)}ms</span>
                <span>{timeAgo(e.timestamp)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
