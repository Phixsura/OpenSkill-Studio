"use client";

interface TrendInfo { endpoint: string; method: string; trend: string; total_requests: number; }
interface Props { trends: TrendInfo[]; growingCount: number; decliningCount: number; appName: string; }

const trendEmoji: Record<string, string> = { growing: "📈", declining: "📉", stable: "➡️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrendCard({ trends, growingCount, decliningCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Usage Trends</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">📈{growingCount} 📉{decliningCount}</span>
      </div>
      {trends.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No trend data</p>
      ) : (
        <div className="space-y-1">
          {trends.map((t) => (
            <div key={`${t.method}-${t.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{trendEmoji[t.trend]} {t.method} {t.endpoint}</span>
              <span className="text-gray-400">{t.total_requests.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
