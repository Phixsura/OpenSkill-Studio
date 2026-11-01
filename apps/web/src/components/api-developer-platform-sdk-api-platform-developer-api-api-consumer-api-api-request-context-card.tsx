"use client";

interface RegionCount { region: string; count: number; }
interface Props { activeContexts: number; regions: RegionCount[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContextCard({ activeContexts, regions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📎 Request Context</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{activeContexts.toLocaleString()}</span>
      </div>
      {regions.length > 0 && (
        <div className="space-y-1">
          {regions.map((r) => (
            <div key={r.region} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">🌍 {r.region}</span>
              <span className="text-gray-400">{r.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
