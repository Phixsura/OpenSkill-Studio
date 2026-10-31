"use client";

interface ApiKeyUsage {
  keyName: string;
  keyPrefix: string;
  callsToday: number;
  callsThisMonth: number;
  quota: number;
  lastUsed: string;
  status: "active" | "rate_limited" | "revoked";
}

interface EndpointUsage {
  endpoint: string;
  method: string;
  calls: number;
  avgLatencyMs: number;
  errorRate: number;
}

export function ApiUsageDashboard({
  keys,
  endpoints,
  totalCalls,
  periodLabel,
}: {
  keys: ApiKeyUsage[];
  endpoints: EndpointUsage[];
  totalCalls: number;
  periodLabel: string;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">📊 API Usage</h2>
        <span className="text-sm text-gray-500">{periodLabel}</span>
      </div>

      <div className="rounded-xl border dark:border-gray-700 p-4">
        <div className="text-3xl font-black">{totalCalls.toLocaleString()}</div>
        <div className="text-sm text-gray-500">Total API calls this period</div>
      </div>

      <div>
        <h3 className="font-semibold mb-3">🔑 API Keys</h3>
        <div className="space-y-2">
          {keys.map((key) => {
            const usagePercent = Math.min(100, Math.round((key.callsToday / key.quota) * 100));
            return (
              <div key={key.keyPrefix} className="rounded-lg border dark:border-gray-700 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-medium">{key.keyName}</span>
                    <span className="text-xs text-gray-400 ml-2 font-mono">{key.keyPrefix}...</span>
                  </div>
                  <StatusBadge status={key.status} />
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mb-1">
                  <div
                    className={`h-1.5 rounded-full ${usagePercent > 90 ? "bg-red-500" : usagePercent > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                    style={{ width: `${usagePercent}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-400">
                  <span>{key.callsToday.toLocaleString()} / {key.quota.toLocaleString()} today</span>
                  <span>Last used: {key.lastUsed}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-3">🔗 Top Endpoints</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b dark:border-gray-700">
                <th className="pb-2">Endpoint</th>
                <th className="pb-2">Method</th>
                <th className="pb-2 text-right">Calls</th>
                <th className="pb-2 text-right">Avg Latency</th>
                <th className="pb-2 text-right">Error Rate</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((ep) => (
                <tr key={`${ep.method}-${ep.endpoint}`} className="border-b dark:border-gray-800">
                  <td className="py-2 font-mono text-xs">{ep.endpoint}</td>
                  <td className="py-2">
                    <MethodBadge method={ep.method} />
                  </td>
                  <td className="py-2 text-right">{ep.calls.toLocaleString()}</td>
                  <td className="py-2 text-right">{ep.avgLatencyMs}ms</td>
                  <td className="py-2 text-right">
                    <span className={ep.errorRate > 5 ? "text-red-500" : "text-green-500"}>
                      {ep.errorRate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    rate_limited: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    revoked: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  };
  return <span className={`text-xs px-2 py-0.5 rounded-full ${colors[status] || ""}`}>{status}</span>;
}

function MethodBadge({ method }: { method: string }) {
  const colors: Record<string, string> = {
    GET: "text-blue-500", POST: "text-green-500",
    PUT: "text-yellow-500", DELETE: "text-red-500",
  };
  return <span className={`font-mono text-xs font-bold ${colors[method] || ""}`}>{method}</span>;
}
