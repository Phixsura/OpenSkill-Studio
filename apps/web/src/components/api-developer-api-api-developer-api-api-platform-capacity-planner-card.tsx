"use client";

interface PlanInfo { resource: string; current_usage: number; max_capacity: number; utilization_pct: number; months_until_full: number; needs_scaling: boolean; unit: string; growth_rate_pct: number; }
interface Props { plans: PlanInfo[]; scalingNeeded: number; appName: string; }

const rIcon: Record<string, string> = { api_capacity: "🚀", webhook_throughput: "📡", storage: "💾", compute: "⚙️" };

export default function APIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlannerCard({ plans, scalingNeeded, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Capacity Planner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {scalingNeeded > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{scalingNeeded} need scaling</span>}
      </div>
      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No capacity plans</p>
      ) : (
        <div className="space-y-2">
          {plans.map((p) => (
            <div key={p.resource}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{rIcon[p.resource] ?? "•"} {p.resource}</span>
                <span className={p.needs_scaling ? "text-orange-600 font-bold" : "text-gray-400"}>{p.utilization_pct}% · {p.months_until_full}mo left</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${p.utilization_pct >= 80 ? "bg-red-500" : p.utilization_pct >= 60 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(p.utilization_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
