"use client";

interface Props { cacheSize: number; hitRate: number; maxEntries: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCacheCard({ cacheSize, hitRate, maxEntries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Response Cache</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${hitRate >= 50 ? "text-green-600 dark:text-green-400" : "text-gray-400"}`}>{hitRate}% hits</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{cacheSize.toLocaleString()}</div><div className="text-gray-400">Cached</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{maxEntries.toLocaleString()}</div><div className="text-gray-400">Max</div></div>
      </div>
    </div>
  );
}
