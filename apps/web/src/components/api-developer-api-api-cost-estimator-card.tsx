"use client";

interface EstimateInfo { tier: string; api_cost: number; webhook_cost: number; storage_cost: number; total_cost: number; }
interface Props { estimates: EstimateInfo[]; recommendedTier: string; appName: string; }

const tierColor: Record<string, string> = { free: "bg-gray-100 text-gray-700", starter: "bg-blue-100 text-blue-700", pro: "bg-purple-100 text-purple-700", enterprise: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIApiCostEstimatorCard({ estimates, recommendedTier, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Cost Estimator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — recommended: {recommendedTier}</p>
      </div>
      <div className="space-y-2">
        {estimates.map((e) => (
          <div key={e.tier} className={`flex items-center justify-between rounded-lg px-3 py-2 ${e.tier === recommendedTier ? "ring-2 ring-green-400 bg-green-50 dark:bg-green-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
            <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${tierColor[e.tier] ?? ""}`}>{e.tier}</span>
            <span className="text-[12px] font-bold text-gray-900 dark:text-gray-100">${e.total_cost.toFixed(2)}/mo</span>
          </div>
        ))}
      </div>
    </div>
  );
}
