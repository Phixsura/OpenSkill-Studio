"use client";

interface Props { consumerId: string; period: string; projectedRequests: number; baseCostCents: number; overageCostCents: number; totalCostCents: number; savingsCents: number; tierName: string; appName: string; }

const fmtCost = (cents: number) => `$${(cents / 100).toFixed(2)}`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiCostEstimatorCard({ consumerId, period, projectedRequests, baseCostCents, overageCostCents, totalCostCents, savingsCents, tierName, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💵 Cost Estimator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {tierName} · {period}</p>
      </div>
      <div className="mb-3 text-center">
        <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{fmtCost(totalCostCents)}</div>
        <div className="text-[10px] text-gray-400">Estimated for {projectedRequests.toLocaleString()} requests</div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="text-gray-700 dark:text-gray-300">{fmtCost(baseCostCents)}</div><div className="text-[10px] text-gray-400">Base</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={overageCostCents > 0 ? "text-amber-600" : "text-gray-700 dark:text-gray-300"}>{fmtCost(overageCostCents)}</div><div className="text-[10px] text-gray-400">Overage</div></div>
      </div>
      {savingsCents > 0 && <div className="mt-2 rounded bg-green-50 p-1.5 text-center text-[10px] text-green-700 dark:bg-green-900/20 dark:text-green-400">💡 Upgrade to save {fmtCost(savingsCents)}/period</div>}
    </div>
  );
}
