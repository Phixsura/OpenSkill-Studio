"use client";

interface Cell { day: string; hour: number; count: number; intensity: number; }
interface Peak { day: string; hour: number; count: number; }
interface ActivityHeatmapGridProps { cells: Cell[]; days: string[]; totalEvents: number; peak: Peak; }

export function ActivityHeatmapGrid({ cells, days, totalEvents, peak }: ActivityHeatmapGridProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Activity Heatmap</h2>
        <span className="text-xs text-gray-400">{totalEvents.toLocaleString()} events</span>
      </div>
      <div className="overflow-x-auto">
        <div className="min-w-[600px]">
          {days.map(day => {
            const row = cells.filter(c => c.day === day);
            return (
              <div key={day} className="flex items-center gap-0.5">
                <span className="w-8 text-xs text-gray-400">{day}</span>
                {row.map(c => (
                  <div key={c.hour} title={`${c.day} ${c.hour}:00 — ${c.count} events`}
                    className="h-4 flex-1 rounded-sm" style={{
                      backgroundColor: c.count === 0 ? "var(--tw-bg-opacity, #f3f4f6)" :
                        `rgba(59, 130, 246, ${Math.max(c.intensity / 100, 0.15)})`,
                    }} />
                ))}
              </div>
            );
          })}
        </div>
      </div>
      <p className="text-center text-xs text-gray-400">
        Peak: {peak.day} at {peak.hour}:00 ({peak.count} events)
      </p>
    </div>
  );
}
