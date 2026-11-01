"use client";

interface ConfigInfo { destination: string; failure_threshold: number; recovery_timeout_seconds: number; half_open_max_requests: number; success_threshold: number; enabled: boolean; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfigCard({ configs, appName }: Props) {
  const enabledCount = configs.filter(c => c.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit Breaker Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {enabledCount}/{configs.length} enabled</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.destination} className={`rounded-lg px-3 py-2 ${c.enabled ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-100 opacity-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(c.destination).hostname}</span>
                <span className="text-gray-400">{c.failure_threshold} fails → open</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">recovery: {c.recovery_timeout_seconds}s · half-open: {c.half_open_max_requests} req / {c.success_threshold} success</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
