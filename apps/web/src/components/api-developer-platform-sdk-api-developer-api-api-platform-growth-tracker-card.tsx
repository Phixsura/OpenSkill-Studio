"use client";

interface SnapshotInfo { period: string; total_consumers: number; new_consumers: number; churned_consumers: number; net_growth: number; churn_rate_pct: number; mrr_cents: number; growth_healthy: boolean; }
interface Props { snapshots: SnapshotInfo[]; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(0)}`; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTrackerCard({ snapshots, appName }: Props) {
  const latest = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Platform Growth</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {latest && <span className={`text-sm font-bold ${latest.growth_healthy ? "text-green-600" : "text-red-500"}`}>{latest.net_growth >= 0 ? "+" : ""}{latest.net_growth} net</span>}
      </div>
      {snapshots.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No growth data</p>
      ) : (
        <div className="space-y-2">
          {snapshots.slice(-3).reverse().map((s) => (
            <div key={s.period} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.period}</span>
                <span className="text-gray-400">{s.total_consumers} consumers · {fmtCents(s.mrr_cents)} MRR</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span className="text-green-600">+{s.new_consumers} new</span>
                <span className="text-red-500">-{s.churned_consumers} churned</span>
                <span>{s.churn_rate_pct}% churn</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
