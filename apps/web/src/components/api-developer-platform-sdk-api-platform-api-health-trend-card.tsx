"use client";

interface DataPointInfo { timestamp: string; health_score: number; uptime_pct: number; error_rate_pct: number; avg_latency_ms: number; }
interface Props { dataPoints: DataPointInfo[]; latestScore: number; avgScore: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiHealthTrendCard({ dataPoints, latestScore, avgScore, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Health Trend</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — avg: {avgScore}</p>
        </div>
        <span className={`text-lg font-bold ${latestScore >= 80 ? "text-green-600" : latestScore >= 50 ? "text-yellow-600" : "text-red-500"}`}>{latestScore}</span>
      </div>
      {dataPoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health trend data</p>
      ) : (
        <div className="space-y-1">
          {dataPoints.slice(-5).reverse().map((dp) => (
            <div key={dp.timestamp} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{dp.timestamp}</span>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span className={dp.health_score >= 80 ? "text-green-600 font-bold" : "text-red-500 font-bold"}>{dp.health_score}</span>
                <span>{dp.uptime_pct}%</span>
                <span>{dp.avg_latency_ms}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
