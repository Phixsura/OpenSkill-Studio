"use client";

interface TargetInfo { endpoint: string; method: string; completed: boolean; latency_ms: number; }
interface Props { planId: string; targets: TargetInfo[]; progressPct: number; isComplete: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmupCard({ planId, targets, progressPct, isComplete, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔥 Endpoint Warmup</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${isComplete ? "text-green-600 dark:text-green-400" : "text-gray-400"}`}>{isComplete ? "✅ Done" : `${progressPct}%`}</span>
      </div>
      <div className="mb-3 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-orange-500" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-1">
        {targets.map((t) => (
          <div key={`${t.method}-${t.endpoint}`} className="flex items-center justify-between text-[11px]">
            <span className={t.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{t.method} {t.endpoint}</span>
            {t.completed && <span className="text-gray-400">{Math.round(t.latency_ms)}ms</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
