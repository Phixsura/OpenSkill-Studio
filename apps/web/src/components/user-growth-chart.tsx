"use client";

interface GrowthMetric { period: string; new_users: number; churned: number;
  net_growth: number; total_users: number; growth_rate: number; }
interface UserGrowthChartProps { metrics: GrowthMetric[]; currentTotal: number;
  avgGrowthRate: number; trend: string; }

const trendIcon: Record<string, string> = { growing: "📈", shrinking: "📉", flat: "➡️" };

export function UserGrowthChart({ metrics, currentTotal, avgGrowthRate, trend }: UserGrowthChartProps) {
  const maxTotal = Math.max(...metrics.map(m => m.total_users), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">User Growth</h2>
        <div className="text-right">
          <span className="text-xl font-bold">{currentTotal.toLocaleString()}</span>
          <p className="text-xs text-gray-400">{trendIcon[trend]} {avgGrowthRate > 0 ? "+" : ""}{avgGrowthRate}%/mo</p>
        </div>
      </div>
      <div className="flex items-end gap-1" style={{ height: "60px" }}>
        {metrics.map(m => (
          <div key={m.period} className="flex-1 rounded-t bg-blue-400 dark:bg-blue-600"
            style={{ height: `${(m.total_users / maxTotal) * 100}%` }}
            title={`${m.period}: ${m.total_users.toLocaleString()}`} />
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b text-gray-400 dark:border-gray-700">
              <th className="pb-1 text-left">Period</th>
              <th className="pb-1 text-right">New</th>
              <th className="pb-1 text-right">Churned</th>
              <th className="pb-1 text-right">Net</th>
              <th className="pb-1 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map(m => (
              <tr key={m.period} className="border-b dark:border-gray-800">
                <td className="py-1">{m.period}</td>
                <td className="py-1 text-right text-green-500">+{m.new_users}</td>
                <td className="py-1 text-right text-red-500">-{m.churned}</td>
                <td className={`py-1 text-right font-bold ${m.net_growth >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {m.net_growth >= 0 ? "+" : ""}{m.net_growth}
                </td>
                <td className="py-1 text-right">{m.total_users.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
