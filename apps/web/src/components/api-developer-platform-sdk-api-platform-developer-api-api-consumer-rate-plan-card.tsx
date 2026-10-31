"use client";

interface PlanInfo { plan_id: string; name: string; requests_per_minute: number; requests_per_day: number; burst_size: number; consumer_count: number; }
interface Props { plans: PlanInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerRatePlanCard({ plans, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Rate Plans</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {plans.length} plans</p>
      </div>
      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate plans</p>
      ) : (
        <div className="space-y-2">
          {plans.map((p) => (
            <div key={p.plan_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-semibold text-gray-700 dark:text-gray-300">{p.name}</span>
                <span className="text-gray-400">{p.consumer_count} consumers</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                {p.requests_per_minute}/min · {p.requests_per_day.toLocaleString()}/day · burst: {p.burst_size}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
