"use client";

interface DepInfo { endpoint: string; replacement: string; days_until_sunset: number; hit_count: number; unique_consumer_count: number; }
interface Props { deprecations: DepInfo[]; pastSunsetCount: number; appName: string; }

export default function APIDeveloperAPIDeprecationTrackerCard({ deprecations, pastSunsetCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Deprecation Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pastSunsetCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{pastSunsetCount} past sunset</span>}
      </div>
      {deprecations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecated endpoints</p>
      ) : (
        <div className="space-y-2">
          {deprecations.map((d) => (
            <div key={d.endpoint} className="rounded-lg bg-yellow-50 p-2 dark:bg-yellow-900/20">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{d.endpoint}</span>
                <span className={d.days_until_sunset < 7 ? "text-red-500 font-bold" : "text-yellow-600"}>{d.days_until_sunset}d left</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                {d.replacement && <span>→ {d.replacement}</span>}
                <span>{d.hit_count} hits · {d.unique_consumer_count} consumers</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
