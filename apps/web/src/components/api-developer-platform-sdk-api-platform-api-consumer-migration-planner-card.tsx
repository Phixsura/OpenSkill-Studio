"use client";

interface PlanInfo { consumer_id: string; from_version: string; to_version: string; complexity: string; status: string; breaking_changes: number; estimated_effort_hours: number; }
interface Props { plans: PlanInfo[]; blockedCount: number; pendingCount: number; appName: string; }

const sColor: Record<string, string> = { planned: "bg-gray-100 text-gray-600", in_progress: "bg-blue-100 text-blue-700", completed: "bg-green-100 text-green-700", blocked: "bg-red-100 text-red-700" };
const cColor: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlannerCard({ plans, blockedCount, pendingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚚 Migration Planner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pendingCount} pending</p>
        </div>
        {blockedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{blockedCount} blocked</span>}
      </div>
      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migration plans</p>
      ) : (
        <div className="space-y-2">
          {plans.slice(0, 5).map((p) => (
            <div key={p.consumer_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}: {p.from_version} → {p.to_version}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${sColor[p.status] ?? ""}`}>{p.status}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span className={cColor[p.complexity] ?? ""}>{p.complexity} complexity</span>
                <span>{p.breaking_changes} breaking</span>
                <span>{p.estimated_effort_hours}h effort</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
