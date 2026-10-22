"use client";

interface Cohort { month: string; installed: number; retained: number; retention_rate: number; }
interface RetentionChartProps { cohorts: Cohort[]; }

export function RetentionChart({ cohorts }: RetentionChartProps) {
  if (cohorts.length === 0) return <p className="text-sm text-gray-400">No retention data yet.</p>;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Retention by Cohort</h3>
      <div className="mt-3 space-y-2">
        {cohorts.map(c => (
          <div key={c.month} className="flex items-center gap-3">
            <span className="w-20 text-xs text-gray-500">{c.month}</span>
            <div className="flex-1">
              <div className="h-4 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${c.retention_rate >= 80 ? "bg-green-500" : c.retention_rate >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${c.retention_rate}%` }} />
              </div>
            </div>
            <span className="w-14 text-right text-xs font-medium">{c.retention_rate}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
