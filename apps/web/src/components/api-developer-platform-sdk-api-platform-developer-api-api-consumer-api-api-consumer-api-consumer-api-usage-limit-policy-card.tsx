"use client";

interface Limit { metric: string; period: string; current: number; max: number; resetAt: string; }
interface Props { limits: Limit[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicyCard({ limits, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Usage Limits</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage limits</p>
      ) : (
        <div className="space-y-2">
          {limits.map((l, i) => {
            const pct = l.max > 0 ? Math.round((l.current / l.max) * 100) : 0;
            return (
              <div key={i} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{l.metric} / {l.period}</span>
                  <span className="text-gray-500">{l.current.toLocaleString()} / {l.max.toLocaleString()}</span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
                <div className="mt-0.5 text-[9px] text-gray-400">Resets: {l.resetAt}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
