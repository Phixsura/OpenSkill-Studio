"use client";

interface MetricSummary { name: string; type: string; value: number | string; }
interface TelemetryCollectDashProps { metrics: MetricSummary[]; totalMetrics: number;
  counters: number; gauges: number; histograms: number; }

const TYPE_BADGE: Record<string, string> = {
  counter: "bg-blue-100 text-blue-700", gauge: "bg-green-100 text-green-700",
  histogram: "bg-purple-100 text-purple-700",
};

export function TelemetryCollectDash({ metrics, totalMetrics, counters, gauges, histograms }: TelemetryCollectDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Telemetry</h3>
        <span className="text-xs text-gray-400">{totalMetrics} metrics · {counters}C {gauges}G {histograms}H</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {metrics.map(m => (
          <div key={m.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1 rounded text-[10px] ${TYPE_BADGE[m.type] ?? ""}`}>{m.type}</span>
              <span className="font-mono">{m.name}</span>
            </div>
            <span className="text-gray-400 font-mono">{m.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
