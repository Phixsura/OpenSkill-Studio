"use client";

interface OverrideInfo { override_id: string; consumer_id: string; endpoint: string; original_rpm: number; override_rpm: number; reason: string; active: boolean; }
interface Props { overrides: OverrideInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverrideCard({ overrides, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Rate Overrides</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{activeCount} active</span>}
      </div>
      {overrides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No overrides</p>
      ) : (
        <div className="space-y-1">
          {overrides.map((o) => (
            <div key={o.override_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{o.consumer_id} → {o.endpoint}</span>
              <span className={o.active ? "text-blue-600 dark:text-blue-400" : "text-gray-400"}>{o.original_rpm}→{o.override_rpm} rpm</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
