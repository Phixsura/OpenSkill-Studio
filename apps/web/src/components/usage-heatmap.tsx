"use client";

interface HeatmapCell {
  day: string;
  hour: number;
  value: number;
}

export function UsageHeatmap({
  data,
  metricName,
  maxValue,
}: {
  data: HeatmapCell[];
  metricName: string;
  maxValue?: number;
}) {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const max = maxValue || Math.max(1, ...data.map((d) => d.value));

  const getCell = (day: string, hour: number) =>
    data.find((d) => d.day === day && d.hour === hour);

  const getColor = (value: number) => {
    const intensity = value / max;
    if (intensity === 0) return "bg-gray-100 dark:bg-gray-800";
    if (intensity < 0.25) return "bg-green-200 dark:bg-green-900/40";
    if (intensity < 0.5) return "bg-green-400 dark:bg-green-700/60";
    if (intensity < 0.75) return "bg-green-500 dark:bg-green-600";
    return "bg-green-700 dark:bg-green-500";
  };

  const totalCalls = data.reduce((sum, d) => sum + d.value, 0);
  const peakCell = data.length > 0 ? data.reduce((a, b) => a.value > b.value ? a : b) : null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🗓️ {metricName} Heatmap</h2>
        <div className="text-xs text-gray-400">
          Total: {totalCalls.toLocaleString()}
          {peakCell && ` · Peak: ${peakCell.day} ${peakCell.hour}:00 (${peakCell.value.toLocaleString()})`}
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-block">
          {/* Hour labels */}
          <div className="flex ml-10 mb-1">
            {hours.filter((h) => h % 3 === 0).map((h) => (
              <div key={h} className="text-xs text-gray-400" style={{ width: "36px", marginLeft: h === 0 ? 0 : `${(3 - 1) * 12}px` }}>
                {h}:00
              </div>
            ))}
          </div>

          {/* Heatmap grid */}
          {days.map((day) => (
            <div key={day} className="flex items-center gap-1 mb-0.5">
              <span className="text-xs text-gray-400 w-8">{day}</span>
              {hours.map((hour) => {
                const cell = getCell(day, hour);
                const value = cell?.value || 0;
                return (
                  <div key={hour} className={`w-3 h-3 rounded-sm ${getColor(value)}`}
                    title={`${day} ${hour}:00 — ${value.toLocaleString()} ${metricName.toLowerCase()}`} />
                );
              })}
            </div>
          ))}

          {/* Legend */}
          <div className="flex items-center gap-1 mt-2 ml-10 text-xs text-gray-400">
            <span>Less</span>
            {["bg-gray-100 dark:bg-gray-800", "bg-green-200", "bg-green-400", "bg-green-500", "bg-green-700"].map((c, i) => (
              <div key={i} className={`w-3 h-3 rounded-sm ${c}`} />
            ))}
            <span>More</span>
          </div>
        </div>
      </div>
    </div>
  );
}
