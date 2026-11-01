"use client";

interface WindowInfo { consumer_id: string; endpoint: string; remaining: number; max_requests: number; usage_pct: number; }
interface Props { windows: WindowInfo[]; blockedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindowCard({ windows, blockedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Rate Limit Windows</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windows.length} windows</p>
        </div>
        {blockedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🚫 {blockedCount} blocked</span>}
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limits configured</p>
      ) : (
        <div className="space-y-1.5">
          {windows.map((w) => (
            <div key={`${w.consumer_id}-${w.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{w.consumer_id} → {w.endpoint}</span>
              <span className={w.usage_pct >= 90 ? "font-medium text-red-600 dark:text-red-400" : "text-gray-400"}>{w.remaining}/{w.max_requests}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
