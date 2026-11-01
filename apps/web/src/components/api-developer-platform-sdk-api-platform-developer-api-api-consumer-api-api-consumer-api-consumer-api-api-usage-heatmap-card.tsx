"use client";

interface Bucket { hour: number; day: number; count: number; }
interface Props { buckets: Bucket[]; peakHour: number; peakDay: number; totalRequests: number; consumerId: string; appName: string; }

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmapCard({ buckets, peakHour, peakDay, totalRequests, consumerId, appName }: Props) {
  const max = Math.max(...buckets.map((b) => b.count), 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗓️ Usage Heatmap</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {totalRequests.toLocaleString()} total</p>
      </div>
      <div className="mb-2 text-[10px] text-gray-400">
        Peak: {DAYS[peakDay]} at {peakHour}:00
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="flex flex-wrap gap-0.5">
          {buckets.slice(0, 28).map((b, i) => {
            const intensity = b.count / max;
            return (
              <div key={i} className="h-3 w-3 rounded-sm" style={{ backgroundColor: `rgba(59,130,246,${Math.max(0.1, intensity)})` }} title={`${DAYS[b.day]} ${b.hour}:00 — ${b.count}`} />
            );
          })}
        </div>
      )}
    </div>
  );
}
