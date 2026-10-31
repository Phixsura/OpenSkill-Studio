"use client";

interface DataPoint { period: string; requests: number; error_rate: number; }
interface Props { data: DataPoint[]; growthRate: number; appName: string; }

export default function APIDeveloperAPIUsageTrendCard({ data, growthRate, appName }: Props) {
  const maxReqs = Math.max(...data.map((d) => d.requests), 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Usage Trend</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${growthRate >= 0 ? "text-green-600" : "text-red-500"}`}>{growthRate > 0 ? "+" : ""}{growthRate}%</span>
      </div>
      {data.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No trend data</p>
      ) : (
        <div className="flex items-end gap-1" style={{ height: "60px" }}>
          {data.map((d) => (
            <div key={d.period} className="flex-1 rounded-t bg-blue-500 dark:bg-blue-600" style={{ height: `${(d.requests / maxReqs) * 100}%`, minHeight: "2px" }} title={`${d.period}: ${d.requests.toLocaleString()}`} />
          ))}
        </div>
      )}
    </div>
  );
}
