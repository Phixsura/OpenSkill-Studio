"use client";

interface PlanRevenue { plan: string; revenue: number; display: string; }
interface RevenueDashboardPageProps { mrrDisplay: string; arrDisplay: string;
  growthPct: number; growthTrend: string; subscribers: number;
  arpuDisplay: string; churnDisplay: string; byPlan: PlanRevenue[]; }

export function RevenueDashboardPage({ mrrDisplay, arrDisplay, growthPct, growthTrend,
  subscribers, arpuDisplay, churnDisplay, byPlan }: RevenueDashboardPageProps) {
  const trendIcon = growthTrend === "up" ? "📈" : growthTrend === "down" ? "📉" : "➡️";
  return (
    <div className="space-y-5">
      <h2 className="text-lg font-bold">💰 Revenue</h2>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold text-green-600">{mrrDisplay}</p>
          <p className="text-xs text-gray-400">MRR</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{arrDisplay}</p>
          <p className="text-xs text-gray-400">ARR</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{trendIcon} {growthPct}%</p>
          <p className="text-xs text-gray-400">Growth</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{subscribers.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Subscribers</p>
        </div>
      </div>
      <div className="flex gap-4 text-sm text-gray-400">
        <span>ARPU: {arpuDisplay}</span>
        <span>Churn: {churnDisplay}</span>
      </div>
      <div>
        <h3 className="text-sm font-semibold mb-2">Revenue by Plan</h3>
        {byPlan.map(p => (
          <div key={p.plan} className="flex justify-between text-sm py-1 capitalize">
            <span>{p.plan}</span><span className="font-medium">{p.display}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
