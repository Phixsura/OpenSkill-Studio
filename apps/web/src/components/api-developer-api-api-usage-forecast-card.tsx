"use client";

interface ForecastInfo { endpoint: string; current_daily_avg: number; trend: string; growth_rate_pct: number; forecast_7d: number; forecast_30d: number; }
interface Props { forecasts: ForecastInfo[]; appName: string; }

const tIcon: Record<string, string> = { growing: "📈", stable: "➡️", declining: "📉" };
const tColor: Record<string, string> = { growing: "text-green-600", stable: "text-gray-500", declining: "text-red-500" };

export default function APIDeveloperAPIApiUsageForecastCard({ forecasts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔮 Usage Forecast</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {forecasts.length} endpoints</p>
      </div>
      {forecasts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No forecast data</p>
      ) : (
        <div className="space-y-2">
          {forecasts.map((f) => (
            <div key={f.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{f.endpoint}</span>
                <span className={tColor[f.trend] ?? ""}>{tIcon[f.trend] ?? ""} {f.growth_rate_pct > 0 ? "+" : ""}{f.growth_rate_pct}%</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>now: {f.current_daily_avg}/day</span>
                <span>7d: {f.forecast_7d}</span>
                <span>30d: {f.forecast_30d}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
