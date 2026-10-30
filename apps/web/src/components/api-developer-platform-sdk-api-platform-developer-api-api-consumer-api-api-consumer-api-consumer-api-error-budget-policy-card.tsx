"use client";

interface Props { consumerId: string; sloTarget: number; budgetRemainingPct: number; burnRate: number; errorRate: number; totalRequests: number; errorCount: number; alert: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicyCard({ consumerId, sloTarget, budgetRemainingPct, burnRate, errorRate, totalRequests, errorCount, alert, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budget</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · SLO: {sloTarget}%</p>
        </div>
        {alert && <span className="rounded bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700 dark:bg-red-900/30 dark:text-red-400">ALERT</span>}
      </div>
      <div className="mb-3">
        <div className="flex justify-between text-[10px] text-gray-400"><span>Budget remaining</span><span>{budgetRemainingPct}%</span></div>
        <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${budgetRemainingPct > 50 ? "bg-green-500" : budgetRemainingPct > 20 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${Math.min(budgetRemainingPct, 100)}%` }} />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
        <div><div className="font-bold text-gray-700 dark:text-gray-300">{errorRate}%</div><div className="text-gray-400">Error rate</div></div>
        <div><div className="font-bold text-gray-700 dark:text-gray-300">{burnRate}/h</div><div className="text-gray-400">Burn rate</div></div>
        <div><div className="font-bold text-gray-700 dark:text-gray-300">{errorCount}/{totalRequests.toLocaleString()}</div><div className="text-gray-400">Errors</div></div>
      </div>
    </div>
  );
}
