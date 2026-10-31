"use client";

interface WindowInfo { endpoint: string; method: string; availability_pct: number; is_up: boolean; current_streak: number; }
interface Props { windows: WindowInfo[]; downCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTrackerCard({ windows, downCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Availability</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {downCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {downCount} down</span>}
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No availability data</p>
      ) : (
        <div className="space-y-1">
          {windows.map((w) => (
            <div key={`${w.method}-${w.endpoint}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${w.is_up ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{w.method} {w.endpoint}</span>
              </div>
              <span className={w.availability_pct >= 99.9 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{w.availability_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
