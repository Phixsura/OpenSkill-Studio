"use client";

interface HeatmapRow { feature: string; hours: number[]; total: number; peakHour: number; }
interface FeatureHeatmapGridProps { features: HeatmapRow[]; peakHourDisplay: string; totalEvents: number; }

export function FeatureHeatmapGrid({ features, peakHourDisplay, totalEvents }: FeatureHeatmapGridProps) {
  const maxVal = Math.max(...features.flatMap(f => f.hours), 1);
  const opacity = (val: number) => Math.max(0.1, val / maxVal);

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔥 Feature Heatmap</h3>
        <div className="text-xs text-gray-400">
          <span>{totalEvents.toLocaleString()} events</span>
          <span className="mx-2">·</span>
          <span>Peak: {peakHourDisplay}</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr>
            <th className="text-left p-1 font-medium w-24">Feature</th>
            {Array.from({ length: 24 }, (_, i) => (
              <th key={i} className="p-1 text-center text-gray-400 w-6">{i}</th>
            ))}
            <th className="text-right p-1 w-12">Total</th>
          </tr></thead>
          <tbody>
            {features.map(f => (
              <tr key={f.feature}>
                <td className="p-1 font-medium truncate max-w-[96px]">{f.feature}</td>
                {f.hours.map((h, i) => (
                  <td key={i} className="p-0.5">
                    <div className="w-5 h-5 rounded-sm bg-blue-500 mx-auto"
                         style={{ opacity: opacity(h) }} title={`${f.feature} @ ${i}:00 — ${h}`} />
                  </td>
                ))}
                <td className="text-right p-1 font-medium">{f.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
