"use client";

interface SparklineInfo { consumer_id: string; metric: string; points: number[]; trend: string; current: number; }
interface Props { sparklines: SparklineInfo[]; appName: string; }

const trendIcon: Record<string, string> = { up: "📈", down: "📉", stable: "➡️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparklineCard({ sparklines, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Sparklines</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      {sparklines.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sparkline data</p>
      ) : (
        <div className="space-y-2">
          {sparklines.map((s) => (
            <div key={`${s.consumer_id}-${s.metric}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id} / {s.metric}</span>
                <span className="text-gray-400">{trendIcon[s.trend] ?? ""} {s.current.toLocaleString()}</span>
              </div>
              <div className="mt-0.5 flex items-end gap-px h-4">
                {s.points.slice(-12).map((v, i) => {
                  const max = Math.max(...s.points.slice(-12), 1);
                  return <div key={i} className="flex-1 rounded-t bg-blue-400 dark:bg-blue-600" style={{ height: `${(v / max) * 100}%` }} />;
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
