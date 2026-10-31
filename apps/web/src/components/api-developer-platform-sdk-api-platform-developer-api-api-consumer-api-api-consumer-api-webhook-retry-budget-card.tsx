"use client";

interface Props { consumerId: string; hourlyUsed: number; hourlyLimit: number; dailyUsed: number; dailyLimit: number; exhausted: boolean; successRate: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudgetCard({ consumerId, hourlyUsed, hourlyLimit, dailyUsed, dailyLimit, exhausted, successRate, appName }: Props) {
  const hPct = hourlyLimit > 0 ? Math.round((hourlyUsed / hourlyLimit) * 100) : 0;
  const dPct = dailyLimit > 0 ? Math.round((dailyUsed / dailyLimit) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Retry Budget</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {exhausted && <span className="rounded bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700 dark:bg-red-900/30 dark:text-red-400">EXHAUSTED</span>}
      </div>
      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-[11px] text-gray-500"><span>Hourly</span><span>{hourlyUsed}/{hourlyLimit}</span></div>
          <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700"><div className={`h-full rounded-full ${hPct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(hPct, 100)}%` }} /></div>
        </div>
        <div>
          <div className="flex justify-between text-[11px] text-gray-500"><span>Daily</span><span>{dailyUsed}/{dailyLimit}</span></div>
          <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700"><div className={`h-full rounded-full ${dPct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(dPct, 100)}%` }} /></div>
        </div>
        <div className="text-[10px] text-gray-400">Success rate: {(successRate * 100).toFixed(0)}%</div>
      </div>
    </div>
  );
}
