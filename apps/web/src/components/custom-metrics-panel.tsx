"use client";
interface MetricDef { name: string; unit: string; count: number; }
interface CustomMetricsPanelProps { metrics: MetricDef[]; }
export function CustomMetricsPanel({ metrics }: CustomMetricsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📐 Custom Metrics</h3>
        <span className="text-xs text-gray-400">{metrics.length} metrics</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {metrics.map(m => (
          <div key={m.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{m.name} <span className="text-gray-400">({m.unit})</span></span>
            <span className="text-gray-400">{m.count.toLocaleString()} points</span>
          </div>
        ))}
      </div>
    </div>
  );
}
