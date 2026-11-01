"use client";

interface TrafficInfo { endpoint: string; method: string; rps: number; error_rate: number; request_count: number; unique_consumers: number; }
interface Props { endpoints: TrafficInfo[]; totalRps: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalyticsCard({ endpoints, totalRps, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Traffic Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{totalRps} rps</span>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traffic data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</span>
                <span className="text-gray-400">{e.rps} rps</span>
              </div>
              <div className="flex gap-3 text-[10px] text-gray-400">
                <span>{e.request_count.toLocaleString()} reqs</span>
                <span className={e.error_rate > 5 ? "text-red-500" : ""}>{e.error_rate}% err</span>
                <span>{e.unique_consumers} consumers</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
