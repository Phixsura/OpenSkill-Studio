"use client";

interface EarningsReportCardProps { totalGross: number; totalFees: number; totalNet: number;
  avgMonthlyNet: number; bestMonth: string | null; avgGrowthPct: number; }

export function EarningsReportCard({ totalGross, totalFees, totalNet, avgMonthlyNet, bestMonth, avgGrowthPct }: EarningsReportCardProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Earnings Report</h2>
      <div className="text-center">
        <p className="text-3xl font-bold text-green-600">${totalNet.toLocaleString()}</p>
        <p className="text-sm text-gray-400">Net Earnings</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="font-bold">${totalGross.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Gross Revenue</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="font-bold text-red-500">-${totalFees.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Platform Fees</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="font-bold">${avgMonthlyNet.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Avg Monthly</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className={`font-bold ${avgGrowthPct >= 0 ? "text-green-600" : "text-red-600"}`}>
            {avgGrowthPct >= 0 ? "+" : ""}{avgGrowthPct}%
          </p>
          <p className="text-xs text-gray-400">Avg Growth</p>
        </div>
      </div>
      {bestMonth && <p className="text-center text-xs text-gray-400">Best month: {bestMonth}</p>}
    </div>
  );
}
