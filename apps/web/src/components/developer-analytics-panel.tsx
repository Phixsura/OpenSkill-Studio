"use client";

interface DailyMetric {
  date: string;
  installs: number;
  uninstalls: number;
  apiCalls: number;
  revenue: number;
}

interface ExtensionMetrics {
  extensionId: string;
  extensionName: string;
  totalInstalls: number;
  activeInstalls: number;
  totalRevenue: number;
  avgRating: number;
}

export function DeveloperAnalyticsPanel({
  dailyMetrics,
  extensions,
  period,
}: {
  dailyMetrics: DailyMetric[];
  extensions: ExtensionMetrics[];
  period: string;
}) {
  const totalInstalls = dailyMetrics.reduce((s, d) => s + d.installs, 0);
  const totalUninstalls = dailyMetrics.reduce((s, d) => s + d.uninstalls, 0);
  const totalApiCalls = dailyMetrics.reduce((s, d) => s + d.apiCalls, 0);
  const totalRevenue = dailyMetrics.reduce((s, d) => s + d.revenue, 0);
  const netInstalls = totalInstalls - totalUninstalls;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📈 Developer Analytics</h2>
        <span className="text-sm text-gray-500">{period}</span>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="Net Installs" value={netInstalls} delta={netInstalls > 0 ? "positive" : "negative"} />
        <MetricCard label="API Calls" value={totalApiCalls} />
        <MetricCard label="Revenue" value={`$${(totalRevenue / 100).toFixed(2)}`} delta="positive" />
        <MetricCard label="Churn" value={totalInstalls > 0 ? `${((totalUninstalls / totalInstalls) * 100).toFixed(1)}%` : "0%"} />
      </div>

      {/* Daily breakdown */}
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h3 className="font-semibold mb-3 text-sm">Daily Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b dark:border-gray-700 text-xs">
                <th className="pb-2">Date</th>
                <th className="pb-2 text-right">Installs</th>
                <th className="pb-2 text-right">Uninstalls</th>
                <th className="pb-2 text-right">API Calls</th>
                <th className="pb-2 text-right">Revenue</th>
              </tr>
            </thead>
            <tbody>
              {dailyMetrics.map((d) => (
                <tr key={d.date} className="border-b dark:border-gray-800 text-xs">
                  <td className="py-1.5">{d.date}</td>
                  <td className="py-1.5 text-right text-green-500">+{d.installs}</td>
                  <td className="py-1.5 text-right text-red-500">{d.uninstalls > 0 ? `-${d.uninstalls}` : "0"}</td>
                  <td className="py-1.5 text-right">{d.apiCalls.toLocaleString()}</td>
                  <td className="py-1.5 text-right">${(d.revenue / 100).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-extension metrics */}
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h3 className="font-semibold mb-3 text-sm">By Extension</h3>
        <div className="space-y-2">
          {extensions.map((ext) => (
            <div key={ext.extensionId} className="flex items-center justify-between text-sm py-1">
              <span className="font-medium">{ext.extensionName}</span>
              <div className="flex gap-4 text-xs text-gray-400">
                <span>{ext.activeInstalls.toLocaleString()} active</span>
                <span>★ {ext.avgRating.toFixed(1)}</span>
                <span className="text-green-500">${(ext.totalRevenue / 100).toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, delta }: { label: string; value: string | number; delta?: string }) {
  return (
    <div className="rounded-lg border dark:border-gray-700 p-3 text-center">
      <div className={`text-xl font-bold ${delta === "positive" ? "text-green-500" : delta === "negative" ? "text-red-500" : ""}`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
