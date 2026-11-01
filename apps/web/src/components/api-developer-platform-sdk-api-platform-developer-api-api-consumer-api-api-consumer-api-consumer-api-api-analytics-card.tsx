"use client";

interface Summary { metric: string; total: number; average: number; min: number; max: number; points: number; trend: string; }
interface Props { summaries: Summary[]; consumerId: string; appName: string; }

const trendIcons: Record<string, string> = { up: "📈", down: "📉", flat: "➡️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalyticsCard({ summaries, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 API Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {summaries.length} metrics</p>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No analytics data</p>
      ) : (
        <div className="space-y-2">
          {summaries.map((s) => (
            <div key={s.metric} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.metric}</span>
                <span>{trendIcons[s.trend]} {s.trend}</span>
              </div>
              <div className="mt-0.5 grid grid-cols-4 gap-1 text-center text-[10px] text-gray-400">
                <span>Total: {s.total.toLocaleString()}</span>
                <span>Avg: {s.average}</span>
                <span>Min: {s.min}</span>
                <span>Max: {s.max}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
