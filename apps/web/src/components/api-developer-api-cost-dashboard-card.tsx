"use client";

interface CostInfo { total_cost: number; budget_limit: number; budget_used_pct: number; projected_monthly: number; cost_trend: string; over_budget: boolean; currency: string; }
interface Props { cost: CostInfo; appName: string; }

const trendIcon: Record<string, string> = { increasing: "📈", decreasing: "📉", stable: "➡️" };

export default function APIDeveloperAPICostDashboardCard({ cost: c, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Cost Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${c.over_budget ? "text-red-500" : "text-gray-900 dark:text-gray-100"}`}>{c.currency} {c.total_cost.toFixed(2)}</span>
          {c.over_budget && <p className="text-[10px] text-red-500">Over budget!</p>}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{c.currency} {c.budget_limit.toFixed(0)}</p>
          <p className="text-[8px] text-gray-500">Budget</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{c.budget_used_pct}%</p>
          <p className="text-[8px] text-gray-500">Used</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{trendIcon[c.cost_trend] ?? ""} {c.cost_trend}</p>
          <p className="text-[8px] text-gray-500">Trend</p>
        </div>
      </div>
    </div>
  );
}
