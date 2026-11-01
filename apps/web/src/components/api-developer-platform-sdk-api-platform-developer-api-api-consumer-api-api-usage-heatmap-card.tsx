"use client";

interface CellData { day: string; hour: number; requests: number; }
interface Props { cells: CellData[]; peakDay: string; peakHour: number; totalRequests: number; appName: string; }

const intensity = (v: number, max: number) => max === 0 ? 0 : Math.round((v / max) * 4);
const colors = ["bg-gray-100 dark:bg-gray-800", "bg-blue-100 dark:bg-blue-900/30", "bg-blue-300 dark:bg-blue-700", "bg-blue-500 dark:bg-blue-500", "bg-blue-700 dark:bg-blue-300"];

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmapCard({ cells, peakDay, peakHour, totalRequests, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Usage Heatmap</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRequests.toLocaleString()} total</p>
        </div>
        <span className="text-[10px] text-gray-400">Peak: {peakDay} {peakHour}:00</span>
      </div>
      <div className="text-center text-[10px] text-gray-400">Visualizes request volume by day and hour</div>
    </div>
  );
}
