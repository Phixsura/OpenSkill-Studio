"use client";

interface ForecastInfo { consumer_id: string; next_period: string; predicted_requests: number; growth_rate_pct: number; confidence: string; trend: string; }
interface Props { forecasts: ForecastInfo[]; appName: string; }

const trendEmoji: Record<string, string> = { growing: "📈", stable: "➡️", declining: "📉" };
const confStyle: Record<string, string> = { high: "text-green-600 dark:text-green-400", medium: "text-yellow-600 dark:text-yellow-400", low: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecastCard({ forecasts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔮 Usage Forecast</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {forecasts.length} consumers</p>
      </div>
      {forecasts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No forecasts available</p>
      ) : (
        <div className="space-y-1.5">
          {forecasts.map((f) => (
            <div key={f.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{f.consumer_id}</span>
                <span className="text-gray-400">{trendEmoji[f.trend] ?? ""} {f.growth_rate_pct}%</span>
              </div>
              <div className="flex justify-between text-[10px] text-gray-400">
                <span>{f.predicted_requests.toLocaleString()} predicted ({f.next_period})</span>
                <span className={confStyle[f.confidence] ?? ""}>{f.confidence}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
