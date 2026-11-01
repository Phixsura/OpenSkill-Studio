"use client";

interface ProfileInfo { consumer_id: string; plan: string; current_spend_cents: number; monthly_budget_cents: number; budget_usage_pct: number; over_budget: boolean; }
interface Props { profiles: ProfileInfo[]; planBreakdown: Record<string, number>; overBudgetCount: number; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(2)}`; }
const planColor: Record<string, string> = { free: "bg-gray-100 text-gray-600", starter: "bg-blue-100 text-blue-700", pro: "bg-purple-100 text-purple-700", enterprise: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIApiDeveloperApiApiConsumerBillingProfileCard({ profiles, planBreakdown, overBudgetCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💳 Billing Profiles</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {overBudgetCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{overBudgetCount} over budget</span>}
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(planBreakdown).map(([plan, count]) => (
          <span key={plan} className={`rounded px-1.5 py-0.5 text-[10px] ${planColor[plan] ?? ""}`}>{plan}: {count}</span>
        ))}
      </div>
      {profiles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No billing profiles</p>
      ) : (
        <div className="space-y-1.5">
          {profiles.slice(0, 5).map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <span className={p.over_budget ? "text-red-500 font-bold" : "text-gray-400"}>{fmtCents(p.current_spend_cents)}{p.monthly_budget_cents > 0 ? ` / ${fmtCents(p.monthly_budget_cents)}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
