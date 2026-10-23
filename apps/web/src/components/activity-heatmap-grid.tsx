"use client";

interface HeatmapRow { day: string; hours: number[]; total: number; }
interface ActivityHeatmapGridProps { grid: HeatmapRow[]; maxValue: number;
  peakDisplay: string; totalEvents: number; }

export function ActivityHeatmapGrid({ grid, maxValue, peakDisplay, totalEvents }: ActivityHeatmapGridProps) {
  const intensity = (val: number) => Math.max(0.05, val / Math.max(maxValue, 1));
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🗓️ Activity Heatmap</h3>
        <div className="text-xs text-gray-400">
          <span>{totalEvents.toLocaleString()} events</span>
          <span className="ml-2">Peak: {peakDisplay}</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead><tr>
            <th className="w-10"></th>
            {Array.from({length: 24}, (_, i) => (
              <th key={i} className="text-[9px] text-gray-400 font-normal px-0.5">{i}</th>
            ))}
            <th className="text-xs text-gray-400 pl-2">Total</th>
          </tr></thead>
          <tbody>
            {grid.map(row => (
              <tr key={row.day}>
                <td className="text-xs text-gray-400 pr-2">{row.day}</td>
                {row.hours.map((h, i) => (
                  <td key={i} className="p-0.5">
                    <div className="w-4 h-4 rounded-sm bg-blue-500" style={{ opacity: intensity(h) }}
                         title={`${row.day} ${i}:00 — ${h}`} />
                  </td>
                ))}
                <td className="text-xs text-gray-400 pl-2">{row.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
