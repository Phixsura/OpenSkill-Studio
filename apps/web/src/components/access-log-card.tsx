"use client";

interface EndpointStat {
  method: string;
  path: string;
  total_requests: number;
  error_count: number;
  avg_response_ms: number;
  p95_response_ms: number;
  error_rate_pct: number;
}

interface AccessLogCardProps {
  endpoints: EndpointStat[];
  appName: string;
  overallErrorRate: number;
  totalRequests: number;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  PATCH: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function AccessLogCard({
  endpoints,
  appName,
  overallErrorRate,
  totalRequests,
}: AccessLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Access Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">{formatNum(totalRequests)} requests</span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              overallErrorRate > 5
                ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
            }`}
          >
            {overallErrorRate.toFixed(1)}% errors
          </span>
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints tracked</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((ep) => (
            <div
              key={`${ep.method}-${ep.path}`}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${METHOD_COLORS[ep.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {ep.method}
                </span>
                <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                  {ep.path}
                </span>
              </div>
              <div className="flex items-center gap-4 text-[11px] text-gray-400">
                <span>{formatNum(ep.total_requests)} req</span>
                <span>avg {ep.avg_response_ms.toFixed(0)}ms</span>
                <span>p95 {ep.p95_response_ms.toFixed(0)}ms</span>
                {ep.error_count > 0 && (
                  <span className="text-red-500">{ep.error_rate_pct.toFixed(1)}% err</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
