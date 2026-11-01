"use client";

interface OriginInfo {
  origin: string;
  request_count: number;
  block_rate: number;
  blocked_count: number;
}

interface APICORSOriginLogCardProps {
  origins: OriginInfo[];
  uniqueCount: number;
  appName: string;
}

export default function APICORSOriginLogCard({ origins, uniqueCount, appName }: APICORSOriginLogCardProps) {
  const blocked = origins.filter((o) => o.blocked_count > 0).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 CORS Origins</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{uniqueCount} origins</span>
          {blocked > 0 && <p className="text-[10px] text-red-500">{blocked} blocked</p>}
        </div>
      </div>

      {origins.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No CORS origins tracked</p>
      ) : (
        <div className="space-y-1">
          {origins.map((o) => (
            <div key={o.origin} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <span className="truncate max-w-[200px] text-xs text-gray-700 dark:text-gray-300">{o.origin}</span>
              <div className="text-[10px] text-gray-400">
                {o.request_count} reqs{o.block_rate > 0 ? ` · ${o.block_rate}% blocked` : ""}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
