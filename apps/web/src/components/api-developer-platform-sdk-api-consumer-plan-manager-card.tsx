"use client";

interface PlanInfo { consumer_id: string; plan: string; limits: Record<string, number>; }
interface Props { consumers: PlanInfo[]; planCounts: Record<string, number>; appName: string; }

const pColor: Record<string, string> = { free: "bg-gray-100 text-gray-600", starter: "bg-blue-100 text-blue-700", pro: "bg-purple-100 text-purple-700", enterprise: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperPlatformSDKApiConsumerPlanManagerCard({ consumers, planCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Consumer Plans</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumers.length} consumers</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(planCounts).map(([plan, count]) => (
          <span key={plan} className={`rounded px-1.5 py-0.5 text-[10px] ${pColor[plan] ?? ""}`}>{plan}: {count}</span>
        ))}
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumers</p>
      ) : (
        <div className="space-y-1">
          {consumers.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className={`rounded px-1.5 py-0.5 text-[9px] ${pColor[c.plan] ?? ""}`}>{c.plan}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
