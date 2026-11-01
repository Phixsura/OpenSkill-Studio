"use client";

interface EndpointHealth {
  endpoint: string; availability: number; avgLatency: number;
  sloTarget: number; sloMet: boolean; errorBudgetRemaining: number; totalRequests: number;
}

export function ApiHealthMonitorPanel({ endpoints }: { endpoints: EndpointHealth[] }) {
  const violations = endpoints.filter((e) => !e.sloMet).length;
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🏥 API Health</h2>
        {violations > 0 ? (
          <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{violations} SLO violations</span>
        ) : (
          <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">All SLOs met</span>
        )}
      </div>
      <div className="space-y-1">
        {endpoints.map((ep) => (
          <div key={ep.endpoint} className={`rounded-lg border-2 p-3 ${ep.sloMet ? "border-green-300 dark:border-green-700" : "border-red-300 dark:border-red-700"}`}>
            <div className="flex items-center justify-between mb-1">
              <code className="text-sm font-semibold">{ep.endpoint}</code>
              <span className={`text-sm font-bold ${ep.sloMet ? "text-green-600" : "text-red-600"}`}>{ep.availability}%</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-500">
              <span>SLO: {ep.sloTarget}%</span>
              <span>{ep.avgLatency}ms avg</span>
              <span>Budget: {ep.errorBudgetRemaining}</span>
              <span>{ep.totalRequests} reqs</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
