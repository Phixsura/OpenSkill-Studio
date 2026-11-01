"use client";

interface IntegrationStatusInfo {
  integration_id: string;
  name: string;
  healthy: boolean;
  availability_pct: number;
  avg_latency_ms: number;
  last_error: string;
}

interface IntegrationHealthCardProps {
  integrations: IntegrationStatusInfo[];
  appName: string;
}

export default function IntegrationHealthCard({
  integrations,
  appName,
}: IntegrationHealthCardProps) {
  const downCount = integrations.filter((i) => !i.healthy).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Integrations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {downCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {downCount} down
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All healthy
          </span>
        )}
      </div>

      {integrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No integrations</p>
      ) : (
        <div className="space-y-2">
          {integrations.map((i) => (
            <div
              key={i.integration_id}
              className={`flex items-center justify-between rounded-lg border px-3 py-2 ${
                i.healthy
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/10"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${i.healthy ? "bg-green-500" : "bg-red-500"}`}
                />
                <div>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{i.name}</span>
                  {i.last_error && <p className="text-[10px] text-red-500">{i.last_error}</p>}
                </div>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-gray-400">
                <span>{i.availability_pct}%</span>
                <span>{i.avg_latency_ms.toFixed(0)}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
