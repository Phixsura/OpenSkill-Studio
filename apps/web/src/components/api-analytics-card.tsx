"use client";

interface EndpointAnalyticsInfo {
  method: string;
  path: string;
  total_requests: number;
  avg_latency_ms: number;
  error_rate_pct: number;
  peak_hour: number | null;
}

interface APIAnalyticsCardProps {
  endpoints: EndpointAnalyticsInfo[];
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function APIAnalyticsCard({ endpoints, appName }: APIAnalyticsCardProps) {
  const totalRequests = endpoints.reduce((s, e) => s + e.total_requests, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{formatNum(totalRequests)} total requests</span>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No analytics data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e) => (
            <div
              key={`${e.method}-${e.path}`}
              className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1 py-0.5 text-[9px] font-bold ${METHOD_COLORS[e.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {e.method}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-gray-400">
                <span>{formatNum(e.total_requests)} req</span>
                <span>{e.avg_latency_ms.toFixed(0)}ms</span>
                {e.error_rate_pct > 0 && (
                  <span className="text-red-500">{e.error_rate_pct}% err</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
