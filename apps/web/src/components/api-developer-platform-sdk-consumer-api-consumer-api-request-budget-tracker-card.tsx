"use client";

interface Props { consumerId: string; dailyUsed: number; dailyBudget: number; dailyPct: number; monthlyUsed: number; monthlyBudget: number; monthlyPct: number; alertTriggered: boolean; blocked: boolean; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTrackerCard({ consumerId, dailyUsed, dailyBudget, dailyPct, monthlyUsed, monthlyBudget, monthlyPct, alertTriggered, blocked, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Request Budget</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {blocked && <span className="rounded bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700 dark:bg-red-900/30 dark:text-red-400">BLOCKED</span>}
        {alertTriggered && !blocked && <span className="rounded bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">ALERT</span>}
      </div>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-[11px]"><span className="text-gray-500">Daily</span><span className="text-gray-700 dark:text-gray-300">{dailyUsed.toLocaleString()} / {dailyBudget.toLocaleString()}</span></div>
          <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700"><div className={`h-full rounded-full ${dailyPct >= 90 ? "bg-red-500" : dailyPct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(dailyPct, 100)}%` }} /></div>
        </div>
        <div>
          <div className="flex justify-between text-[11px]"><span className="text-gray-500">Monthly</span><span className="text-gray-700 dark:text-gray-300">{monthlyUsed.toLocaleString()} / {monthlyBudget.toLocaleString()}</span></div>
          <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700"><div className={`h-full rounded-full ${monthlyPct >= 90 ? "bg-red-500" : monthlyPct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(monthlyPct, 100)}%` }} /></div>
        </div>
      </div>
    </div>
  );
}
