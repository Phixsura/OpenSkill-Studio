"use client";

interface Cohort { period: string; initial_users: number; retention_rates: number[];
  day_30: number | null; day_90: number | null; }
interface RetentionCohortTableProps { cohorts: Cohort[]; avgDay30: number | null; avgDay90: number | null; }

const rateColor = (pct: number) => pct >= 50 ? "bg-green-100 dark:bg-green-900/30" : pct >= 30 ? "bg-yellow-100 dark:bg-yellow-900/30" : "bg-red-100 dark:bg-red-900/30";

export function RetentionCohortTable({ cohorts, avgDay30, avgDay90 }: RetentionCohortTableProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Retention Cohorts</h2>
        <div className="flex gap-3 text-xs text-gray-400">
          {avgDay30 != null && <span>D30: <strong>{avgDay30}%</strong></span>}
          {avgDay90 != null && <span>D90: <strong>{avgDay90}%</strong></span>}
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="pb-2 text-left">Cohort</th>
              <th className="pb-2 text-right">Users</th>
              {Array.from({length: 8}, (_, i) => (
                <th key={i} className="pb-2 text-center">W{i+1}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cohorts.map(c => (
              <tr key={c.period} className="border-b dark:border-gray-800">
                <td className="py-1.5 font-medium">{c.period}</td>
                <td className="py-1.5 text-right text-gray-400">{c.initial_users.toLocaleString()}</td>
                {c.retention_rates.slice(0, 8).map((rate, i) => (
                  <td key={i} className={`py-1.5 text-center ${rateColor(rate)}`}>{rate}%</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
