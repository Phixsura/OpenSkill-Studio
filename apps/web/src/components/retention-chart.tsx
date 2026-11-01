"use client";

interface Cohort { cohort: string; size: number; weeklyRetention: number[]; }
interface RetentionChartProps { cohorts: Cohort[]; avgWeek1: number; avgWeek4: number; }

export function RetentionChart({ cohorts, avgWeek1, avgWeek4 }: RetentionChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">📊 Retention Cohorts</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>W1: {avgWeek1}%</span>
          <span>W4: {avgWeek4}%</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="border-b dark:border-gray-700">
            <th className="px-2 py-1.5 text-left">Cohort</th>
            <th className="px-2 py-1.5 text-right">Size</th>
            {[1, 2, 3, 4].map(w => <th key={w} className="px-2 py-1.5 text-center">W{w}</th>)}
          </tr></thead>
          <tbody>{cohorts.map(c => (
            <tr key={c.cohort} className="border-b dark:border-gray-800">
              <td className="px-2 py-1.5 font-mono">{c.cohort}</td>
              <td className="px-2 py-1.5 text-right">{c.size}</td>
              {c.weeklyRetention.slice(0, 4).map((pct, i) => (
                <td key={i} className="px-2 py-1.5 text-center">
                  <span className={`rounded px-1.5 py-0.5 ${pct >= 50 ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-600 dark:bg-red-900/30"}`}>{pct}%</span>
                </td>
              ))}
            </tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  );
}
