"use client";

interface EstimateInfo { tier: string; total_dollars: string; base_dollars: string; per_request: string; }
interface Props { estimates: EstimateInfo[]; requestCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCostEstimatorCard({ estimates, requestCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Cost Estimator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {requestCount.toLocaleString()} requests/mo</p>
      </div>
      {estimates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pricing data</p>
      ) : (
        <div className="space-y-1.5">
          {estimates.map((e) => (
            <div key={e.tier} className="flex items-center justify-between rounded-lg bg-gray-50 p-2 text-[11px] dark:bg-gray-800">
              <span className="font-semibold text-gray-700 dark:text-gray-300">{e.tier}</span>
              <span className="font-bold text-gray-900 dark:text-gray-100">{e.total_dollars}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
