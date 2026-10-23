"use client";

interface HeatmapRow { day: string; hours: number[]; total: number; }
interface UsageHeatmapProps { rows: HeatmapRow[]; peakHour: number; }

export function UsageHeatmap({ rows, peakHour }: UsageHeatmapProps) {
  const maxVal = Math.max(...rows.flatMap(r => r.hours), 1);
  const intensity = (v: number) => {
    const pct = v / maxVal;
    return pct > 0.8 ? "bg-blue-700" : pct > 0.5 ? "bg-blue-500" : pct > 0.2 ? "bg-blue-300" : pct > 0 ? "bg-blue-100" : "bg-gray-50 dark:bg-gray-800";
  };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">API Usage Heatmap</h3>
        <span className="text-xs text-gray-400">Peak: {peakHour}:00</span>
      </div>
      <div className="mt-3 space-y-1">
        {rows.map(r => (
          <div key={r.day} className="flex items-center gap-1">
            <span className="w-8 text-xs text-gray-400">{r.day}</span>
            {r.hours.map((v, h) => (
              <div key={h} className={`h-3 w-3 rounded-sm ${intensity(v)}`} title={`${r.day} ${h}:00`} />
            ))}
            <span className="ml-1 text-xs text-gray-400">{r.total}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
