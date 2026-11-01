"use client";

interface BreakerInfo { consumer_id: string; state: string; failure_count: number; success_count: number; }
interface Props { breakers: BreakerInfo[]; openCount: number; appName: string; }

const stateStyle: Record<string, string> = { closed: "text-green-600 dark:text-green-400", open: "text-red-600 dark:text-red-400", half_open: "text-yellow-600 dark:text-yellow-400" };
const stateEmoji: Record<string, string> = { closed: "🟢", open: "🔴", half_open: "🟡" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreakerCard({ breakers, openCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit Breakers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {breakers.length} consumers</p>
        </div>
        {openCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {openCount} open</span>}
      </div>
      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers</p>
      ) : (
        <div className="space-y-1">
          {breakers.map((b) => (
            <div key={b.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{stateEmoji[b.state] ?? "⚪"}</span>
                <span className="text-gray-700 dark:text-gray-300">{b.consumer_id}</span>
              </div>
              <span className={stateStyle[b.state] ?? "text-gray-400"}>{b.state} ({b.failure_count}F/{b.success_count}S)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
