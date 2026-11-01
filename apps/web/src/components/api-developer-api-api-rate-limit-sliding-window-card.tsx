"use client";

interface WindowInfo { consumer_id: string; endpoint: string; current: number; max: number; remaining: number; is_limited: boolean; }
interface Props { windows: WindowInfo[]; limitedCount: number; appName: string; }

export default function APIDeveloperAPIApiRateLimitSlidingWindowCard({ windows, limitedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🪟 Sliding Window</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {limitedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{limitedCount} limited</span>}
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limits</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w, i) => (
            <div key={i}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{w.consumer_id} → {w.endpoint}</span>
                <span className={w.is_limited ? "text-red-500 font-bold" : "text-gray-400"}>{w.current}/{w.max}</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${w.is_limited ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${Math.min(w.current / w.max * 100, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
