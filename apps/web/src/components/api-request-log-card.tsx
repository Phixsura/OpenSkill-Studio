"use client";

interface PathStat {
  path: string;
  count: number;
  avg_ms: number;
}

interface APIRequestLogCardProps {
  pathStats: PathStat[];
  totalCount: number;
  errorCount: number;
  appName: string;
}

export default function APIRequestLogCard({ pathStats, totalCount, errorCount, appName }: APIRequestLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Request Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{totalCount.toLocaleString()} requests</span>
          {errorCount > 0 && <p className="text-[10px] text-red-500">{errorCount} errors</p>}
        </div>
      </div>

      {pathStats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No requests logged</p>
      ) : (
        <div className="space-y-1">
          {pathStats.map((p) => (
            <div key={p.path} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <span className="font-mono text-[11px] text-gray-700 dark:text-gray-300">{p.path}</span>
              <span className="text-[10px] text-gray-400">{p.count} · {p.avg_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
