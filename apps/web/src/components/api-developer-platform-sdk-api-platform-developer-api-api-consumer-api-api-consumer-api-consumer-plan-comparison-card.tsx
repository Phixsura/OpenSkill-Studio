"use client";

interface PlanInfo { plan_id: string; name: string; price_dollars: string; requests: number; rps: number; features: string[]; support: string; }
interface Props { plans: PlanInfo[]; recommendedId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerPlanComparisonCard({ plans, recommendedId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💳 Plan Comparison</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {plans.length} plans</p>
      </div>
      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No plans available</p>
      ) : (
        <div className="space-y-2">
          {plans.map((p) => (
            <div key={p.plan_id} className={`rounded-lg p-2 text-[11px] ${p.plan_id === recommendedId ? "border border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-gray-700 dark:text-gray-300">{p.name}{p.plan_id === recommendedId ? " ⭐" : ""}</span>
                <span className="font-bold text-gray-900 dark:text-gray-100">{p.price_dollars}/mo</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{p.requests.toLocaleString()} requests · {p.rps} rps · {p.support}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
