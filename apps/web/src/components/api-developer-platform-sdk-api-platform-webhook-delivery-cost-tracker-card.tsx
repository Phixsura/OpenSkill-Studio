"use client";

interface CostInfo { destination: string; total_deliveries: number; total_cost_cents: number; avg_cost_cents: number; retry_cost_pct: number; }
interface Props { costs: CostInfo[]; totalCostCents: number; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(2)}`; }

export default function APIDeveloperPlatformSDKApiPlatformWebhookDeliveryCostTrackerCard({ costs, totalCostCents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Delivery Costs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-green-600">{fmtCents(totalCostCents)}</span>
      </div>
      {costs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No cost data</p>
      ) : (
        <div className="space-y-1.5">
          {costs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(c.destination).hostname}</span>
              <span className="text-gray-400">{fmtCents(c.total_cost_cents)} · {c.total_deliveries.toLocaleString()} del{c.retry_cost_pct > 0 ? ` · ${c.retry_cost_pct}% retries` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
