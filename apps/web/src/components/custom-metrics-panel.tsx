"use client";

interface MetricInfo { name: string; type: string; current: number; unit: string; dataPoints: number; }
interface CustomMetricsPanelProps { metrics: MetricInfo[]; }

const TYPE_ICON: Record<string, string> = { counter: "🔢", gauge: "📊", histogram: "📈" };

export function CustomMetricsPanel({ metrics }: CustomMetricsPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📐 Custom Metrics</h3>
      <div className="space-y-2">
        {metrics.map(m => (
          <div key={m.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span>{TYPE_ICON[m.type] || "📌"}</span>
                <span className="text-sm font-mono font-medium">{m.name}</span>
                <span className="text-xs text-gray-400">{m.type}</span>
              </div>
              <p className="text-xs text-gray-400 ml-6">{m.dataPoints} data points</p>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold">{m.current.toLocaleString()}</p>
              {m.unit && <p className="text-xs text-gray-400">{m.unit}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
