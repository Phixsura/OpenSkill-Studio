"use client";

interface HealthEndpointInfo {
  endpoint_id: string;
  url: string;
  current_status: "up" | "down" | "degraded" | null;
  uptime_pct: number;
  avg_latency_ms: number;
}

interface HealthCheckCardProps {
  endpoints: HealthEndpointInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  up: "bg-green-500",
  down: "bg-red-500",
  degraded: "bg-yellow-500",
};

export default function HealthCheckCard({ endpoints, appName }: HealthCheckCardProps) {
  const downCount = endpoints.filter((e) => e.current_status === "down").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            💓 Health Checks
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
          {downCount > 0 && (
            <p className="text-[10px] font-medium text-red-600 dark:text-red-400">
              {downCount} down
            </p>
          )}
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health checks</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((e) => (
            <div
              key={e.endpoint_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${e.current_status ? (statusStyle[e.current_status] ?? "bg-gray-400") : "bg-gray-400"}`}
                  />
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                    {e.endpoint_id}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">{e.uptime_pct}% uptime</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span className="max-w-[180px] truncate">{e.url}</span>
                <span>{e.avg_latency_ms}ms avg</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
