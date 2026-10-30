"use client";

interface HistoryPoint { period: string; requests: number; }
interface Props { consumerId: string; history: HistoryPoint[]; predictedRequests: number; nextPeriod: string; trend: string; confidence: number; growthRate: number; appName: string; }

const trendIcons: Record<string, string> = { increasing: "📈", stable: "➡️", decreasing: "📉" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecastCard({ consumerId, history, predictedRequests, nextPeriod, trend, confidence, growthRate, appName }: Props) {
  const max = Math.max(...history.map((h) => h.requests), predictedRequests, 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔮 Usage Forecast</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 flex items-center gap-3 text-[11px]">
        <span>{trendIcons[trend]} {trend}</span>
        <span className="text-gray-400">Growth: {growthRate > 0 ? "+" : ""}{growthRate}%</span>
        <span className="text-gray-400">Confidence: {(confidence * 100).toFixed(0)}%</span>
      </div>
      <div className="flex items-end gap-1" style={{ height: 60 }}>
        {history.map((h) => (
          <div key={h.period} className="flex flex-1 flex-col items-center gap-0.5">
            <div className="w-full rounded-t bg-blue-400" style={{ height: `${(h.requests / max) * 50}px` }} />
            <span className="text-[8px] text-gray-400">{h.period.slice(5)}</span>
          </div>
        ))}
        <div className="flex flex-1 flex-col items-center gap-0.5">
          <div className="w-full rounded-t border-2 border-dashed border-blue-300 bg-blue-100 dark:bg-blue-900/20" style={{ height: `${(predictedRequests / max) * 50}px` }} />
          <span className="text-[8px] font-bold text-blue-500">{nextPeriod.slice(5)}</span>
        </div>
      </div>
      <div className="mt-2 text-center text-[11px] text-gray-500">
        Predicted: <span className="font-bold text-gray-700 dark:text-gray-300">{predictedRequests.toLocaleString()}</span> requests
      </div>
    </div>
  );
}
