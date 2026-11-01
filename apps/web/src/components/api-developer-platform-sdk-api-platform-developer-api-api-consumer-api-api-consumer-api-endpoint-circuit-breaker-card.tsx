"use client";

interface Breaker { path: string; state: string; failures: number; threshold: number; }
interface Props { breakers: Breaker[]; appName: string; }

const stateColors: Record<string, string> = {
  closed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  open: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  half_open: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreakerCard({ breakers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit Breakers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {breakers.length} endpoints</p>
      </div>
      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers</p>
      ) : (
        <div className="space-y-2">
          {breakers.map((b) => (
            <div key={b.path} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <code className="text-[11px] text-gray-700 dark:text-gray-300">{b.path}</code>
                <div className="text-[10px] text-gray-400">{b.failures}/{b.threshold} failures</div>
              </div>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${stateColors[b.state] ?? ""}`}>{b.state}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
