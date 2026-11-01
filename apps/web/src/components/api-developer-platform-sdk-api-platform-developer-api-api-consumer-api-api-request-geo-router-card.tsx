"use client";

interface BackendInfo { region: string; healthy: boolean; latency_ms: number; load_pct: number; }
interface Props { backends: BackendInfo[]; defaultRegion: string; healthyRegionCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouterCard({ backends, defaultRegion, healthyRegionCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Geo Router</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — default: {defaultRegion}</p>
        </div>
        <span className="text-[10px] text-gray-400">{healthyRegionCount} regions up</span>
      </div>
      {backends.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backends</p>
      ) : (
        <div className="space-y-1">
          {backends.map((b) => (
            <div key={b.region} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${b.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{b.region}</span>
              </div>
              <span className="text-gray-400">{b.load_pct}% load · {b.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
