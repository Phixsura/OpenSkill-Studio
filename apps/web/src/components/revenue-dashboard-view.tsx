"use client";

interface MonthlyData { month: string; revenue: number; fees: number; }
interface RevenueDashboardViewProps { totalRevenue: number; netRevenue: number; totalFees: number;
  mrr: number; arr: number; avgMonthlyGrowth: number; monthlyData: MonthlyData[]; }

export function RevenueDashboardView({ totalRevenue, netRevenue, totalFees, mrr, arr,
  avgMonthlyGrowth, monthlyData }: RevenueDashboardViewProps) {
  const maxRev = Math.max(...monthlyData.map(m => m.revenue), 1);
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Revenue Dashboard</h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "MRR", value: `$${mrr.toLocaleString()}`, color: "text-green-600" },
          { label: "ARR", value: `$${arr.toLocaleString()}`, color: "text-blue-600" },
          { label: "Net Revenue", value: `$${netRevenue.toLocaleString()}`, color: "text-purple-600" },
          { label: "Growth", value: `${avgMonthlyGrowth > 0 ? "+" : ""}${avgMonthlyGrowth}%/mo`, color: avgMonthlyGrowth >= 0 ? "text-green-600" : "text-red-600" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="flex items-end gap-1" style={{ height: "80px" }}>
        {monthlyData.map(m => (
          <div key={m.month} className="group relative flex-1">
            <div className="rounded-t bg-green-400 dark:bg-green-600"
              style={{ height: `${(m.revenue / maxRev) * 100}%` }}
              title={`${m.month}: $${m.revenue.toLocaleString()}`} />
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        {monthlyData.length > 0 && <span>{monthlyData[0].month}</span>}
        {monthlyData.length > 1 && <span>{monthlyData[monthlyData.length - 1].month}</span>}
      </div>
    </div>
  );
}
