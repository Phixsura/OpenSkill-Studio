"use client";

interface AccessLogInfo {
  log_id: string;
  actor: string;
  method: string;
  path: string;
  status_code: number;
  ip_address: string;
}

interface APIAccessLogCardProps {
  entries: AccessLogInfo[];
  uniqueActors: number;
  totalCount: number;
  appName: string;
}

export default function APIAccessLogCard({ entries, uniqueActors, totalCount, appName }: APIAccessLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Access Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} entries · {uniqueActors} actors</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No access logs</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.log_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2 text-[11px]">
                <span className="text-gray-500">{e.actor}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{e.method}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className={`text-[10px] ${e.status_code < 400 ? "text-green-600" : "text-red-500"}`}>{e.status_code}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
