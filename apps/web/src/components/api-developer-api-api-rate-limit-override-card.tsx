"use client";

interface OverrideInfo { override_id: string; consumer_id: string; endpoint: string; limit_per_minute: number; reason: string; expired: boolean; }
interface Props { overrides: OverrideInfo[]; appName: string; }

export default function APIDeveloperAPIApiRateLimitOverrideCard({ overrides, appName }: Props) {
  const activeCount = overrides.filter(o => !o.expired).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Rate Limit Overrides</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
      </div>
      {overrides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No overrides</p>
      ) : (
        <div className="space-y-2">
          {overrides.map((o) => (
            <div key={o.override_id} className={`rounded-lg px-3 py-2 ${o.expired ? "bg-gray-100 opacity-50 dark:bg-gray-800" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{o.consumer_id}</span>
                <span className="font-bold text-blue-600">{o.limit_per_minute.toLocaleString()}/min</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{o.endpoint === "*" ? "all endpoints" : o.endpoint} · {o.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
