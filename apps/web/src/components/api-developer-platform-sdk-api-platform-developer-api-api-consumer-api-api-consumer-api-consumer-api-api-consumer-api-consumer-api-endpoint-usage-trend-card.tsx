"use client";

interface Period { period: string; requests: number; errors: number; avgMs: number; }
interface Props { endpointPath: string; periods: Period[]; trendDirection: string; growthRate: number; appName: string; }

const trendIcons: Record<string, string> = { growing: "📈", declining: "📉", stable: "➡️", volatile: "📊" };
const trendColors: Record<string, string> = { growing: "text-green-600", declining: "text-red-600", stable: "text-gray-500", volatile: "text-amber-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrendCard({ endpointPath, periods, trendDirection, growthRate, appName }: Props) {
  const max = Math.max(...periods.map((p) => p.requests), 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Usage Trend</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpointPath}</code></p>
        </div>
        <span className={`text-[11px] font-medium ${trendColors[trendDirection] ?? ""}`}>{trendIcons[trendDirection] ?? ""} {trendDirection} ({growthRate > 0 ? "+" : ""}{growthRate}%)</span>
      </div>
      {periods.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="flex items-end gap-1" style={{ height: 50 }}>
          {periods.map((p) => (
            <div key={p.period} className="flex flex-1 flex-col items-center gap-0.5">
              <div className="w-full rounded-t bg-blue-400" style={{ height: `${(p.requests / max) * 45}px` }} />
              <span className="text-[7px] text-gray-400">{p.period.slice(-2)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
