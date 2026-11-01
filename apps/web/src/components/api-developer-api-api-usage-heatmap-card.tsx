"use client";

interface BucketInfo { day_of_week: number; hour: number; request_count: number; }
interface Props { buckets: BucketInfo[]; peakHour: { day_of_week: number; hour: number; request_count: number } | null; totalRequests: number; appName: string; }

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function APIDeveloperAPIApiUsageHeatmapCard({ buckets, peakHour, totalRequests, appName }: Props) {
  const maxCount = Math.max(1, ...buckets.map(b => b.request_count));
  const intensity = (count: number) => {
    const pct = count / maxCount;
    return pct > 0.75 ? "bg-green-600" : pct > 0.5 ? "bg-green-400" : pct > 0.25 ? "bg-green-200" : pct > 0 ? "bg-green-100" : "bg-gray-100 dark:bg-gray-800";
  };
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Usage Heatmap</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRequests.toLocaleString()} total</p>
        </div>
        {peakHour && <span className="text-[10px] text-gray-400">Peak: {DAYS[peakHour.day_of_week]} {peakHour.hour}:00</span>}
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="grid grid-cols-12 gap-0.5">
          {DAYS.map((day, di) => (
            Array.from({ length: 12 }, (_, hi) => {
              const hour = hi * 2;
              const b = buckets.find(b => b.day_of_week === di && b.hour === hour);
              return <div key={`${di}-${hour}`} className={`h-3 rounded-sm ${intensity(b?.request_count ?? 0)}`} title={`${day} ${hour}:00 — ${b?.request_count ?? 0}`} />;
            })
          ))}
        </div>
      )}
    </div>
  );
}
