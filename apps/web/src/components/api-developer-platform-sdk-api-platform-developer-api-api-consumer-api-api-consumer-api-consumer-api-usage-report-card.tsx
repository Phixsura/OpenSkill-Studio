"use client";

interface Metric { metric: string; value: number; unit: string; changePct: number; }
interface Report { id: string; period: string; metrics: Metric[]; costCents: number; status: string; }
interface Props { reports: Report[]; consumerId: string; totalCostCents: number; appName: string; }

const fmtCost = (cents: number) => `$${(cents / 100).toFixed(2)}`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReportCard({ reports, consumerId, totalCostCents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Reports</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="text-[11px] font-bold text-gray-700 dark:text-gray-300">Total: {fmtCost(totalCostCents)}</span>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No reports</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.period}</span>
                <span className="text-gray-500">{fmtCost(r.costCents)}</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-2 text-[10px] text-gray-400">
                {r.metrics.map((m) => (
                  <span key={m.metric}>{m.metric}: {m.value.toLocaleString()} {m.unit} <span className={m.changePct > 0 ? "text-green-500" : m.changePct < 0 ? "text-red-500" : ""}>{m.changePct > 0 ? "+" : ""}{m.changePct}%</span></span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
