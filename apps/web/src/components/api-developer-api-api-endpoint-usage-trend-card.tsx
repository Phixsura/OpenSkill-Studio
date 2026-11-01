"use client";

interface TrendInfo { endpoint: string; total: number; avg_daily: number; trend_direction: string; }
interface Props { trends: TrendInfo[]; growingCount: number; decliningCount: number; appName: string; }

const tIcon: Record<string, string> = { growing: "📈", stable: "➡️", declining: "📉", unknown: "❓" };
const tColor: Record<string, string> = { growing: "text-green-600", stable: "text-gray-500", declining: "text-red-500" };

export default function APIDeveloperAPIApiEndpointUsageTrendCard({ trends, growingCount, decliningCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Usage Trends</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2 text-[10px]">
          <span className="text-green-600">{growingCount} growing</span>
          <span className="text-red-500">{decliningCount} declining</span>
        </div>
      </div>
      {trends.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No trend data</p>
      ) : (
        <div className="space-y-1.5">
          {trends.map((t) => (
            <div key={t.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{t.endpoint}</span>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">{t.avg_daily}/day</span>
                <span className={tColor[t.trend_direction] ?? ""}>{tIcon[t.trend_direction] ?? ""}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
