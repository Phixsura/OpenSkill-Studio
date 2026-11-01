"use client";

interface StateInfo { consumer_id: string; base_rate: number; current_rate: number; backoff_factor: number; throttled_count: number; }
interface Props { states: StateInfo[]; throttledCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiRequestThrottleCard({ states, throttledCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Request Throttle</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {throttledCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{throttledCount} throttled</span>}
      </div>
      {states.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throttle configs</p>
      ) : (
        <div className="space-y-2">
          {states.map((s) => (
            <div key={s.consumer_id}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
                <span className={s.current_rate < s.base_rate ? "text-orange-600 font-bold" : "text-gray-400"}>{s.current_rate}/{s.base_rate} rps</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${s.current_rate < s.base_rate ? "bg-orange-500" : "bg-green-500"}`} style={{ width: `${(s.current_rate / s.base_rate) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
