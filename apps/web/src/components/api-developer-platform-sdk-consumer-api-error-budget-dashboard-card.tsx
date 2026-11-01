"use client";

interface Entry { endpoint: string; sloTarget: number; remaining: number; burnRate: number; }
interface Props { entries: Entry[]; overallPct: number; atRisk: number; exhausted: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiErrorBudgetDashboardCard({ entries, overallPct, atRisk, exhausted, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budget</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${overallPct > 50 ? "text-green-600" : overallPct > 20 ? "text-amber-600" : "text-red-600"}`}>{overallPct}%</div>
          {(atRisk > 0 || exhausted > 0) && <div className="text-[9px] text-gray-400">{exhausted > 0 ? `${exhausted} exhausted` : ""}{atRisk > 0 ? ` ${atRisk} at risk` : ""}</div>}
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.endpoint}>
              <div className="flex justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{e.endpoint}</code>
                <span className="text-gray-400">SLO: {e.sloTarget}% · Burn: {e.burnRate}x</span>
              </div>
              <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${e.remaining > 50 ? "bg-green-500" : e.remaining > 20 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${Math.max(e.remaining, 0)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
