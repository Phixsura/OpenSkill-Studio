"use client";

interface Request { correlationId: string; method: string; path: string; status: number; latencyMs: number; service: string; isChild: boolean; }
interface Props { requests: Request[]; rootId: string; totalLatencyMs: number; serviceCount: number; appName: string; }

const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelationCard({ requests, rootId, totalLatencyMs, serviceCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Request Correlation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {serviceCount} services · {totalLatencyMs}ms total</p>
      </div>
      {requests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No correlated requests</p>
      ) : (
        <div className="space-y-0.5">
          {requests.map((r) => (
            <div key={r.correlationId} className={`flex items-center justify-between text-[10px] ${r.isChild ? "ml-4" : ""}`}>
              <div className="flex items-center gap-1">
                {r.isChild && <span className="text-gray-300">↳</span>}
                <span className={`font-bold ${methodColors[r.method] ?? "text-gray-500"}`}>{r.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{r.path}</code>
                {r.service && <span className="rounded bg-gray-200 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-700">{r.service}</span>}
              </div>
              <div className="flex gap-2">
                <span className={r.status < 400 ? "text-green-500" : "text-red-500"}>{r.status}</span>
                <span className="text-gray-400">{r.latencyMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
