"use client";

interface MapInfo { consumer_id: string; total_activity: number; peak_hour: number; peak_day: number; }
interface Props { maps: MapInfo[]; appName: string; }

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function APIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmapCard({ maps, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Activity Heatmap</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {maps.length} consumers</p>
      </div>
      {maps.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No activity data</p>
      ) : (
        <div className="space-y-1">
          {maps.slice(0, 5).map((m) => (
            <div key={m.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{m.consumer_id}</span>
              <span className="text-gray-400">{m.total_activity.toLocaleString()} · peak {m.peak_hour}:00 {DAYS[m.peak_day]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
