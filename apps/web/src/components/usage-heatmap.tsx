"use client";

interface HeatmapCell { day: number; hour: number; count: number; intensity: number; }
interface UsageHeatmapProps { cells: HeatmapCell[]; totalEvents: number; peakHour: number; peakDay: number; }

const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function UsageHeatmap({ cells, totalEvents, peakHour, peakDay }: UsageHeatmapProps) {
  const grid = Array.from({ length: 7 }, (_, d) =>
    cells.filter(c => c.day === d).sort((a, b) => a.hour - b.hour)
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Usage Heatmap</h3>
        <span className="text-xs text-gray-400">{totalEvents.toLocaleString()} events · peak {days[peakDay]} {peakHour}:00</span>
      </div>
      <div className="space-y-1">
        {grid.map((row, d) => (
          <div key={d} className="flex items-center gap-1">
            <span className="w-8 text-xs text-gray-400">{days[d]}</span>
            <div className="flex gap-px">
              {row.map(c => (
                <div key={c.hour} title={`${days[c.day]} ${c.hour}:00 — ${c.count} events`}
                  className="h-3 w-3 rounded-sm"
                  style={{ backgroundColor: `rgba(59, 130, 246, ${c.intensity / 100})` }} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
