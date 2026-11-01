"use client";

interface HealthInfo { endpoint: string; consumer_id: string; healthy: boolean; availability: number; consecutive_failures: number; }
interface Props { endpoints: HealthInfo[]; unhealthyCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheckCard({ endpoints, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💓 Webhook Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {unhealthyCount} down</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health data</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${e.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{e.consumer_id}</span>
              </div>
              <span className={e.availability >= 99 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{e.availability}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
