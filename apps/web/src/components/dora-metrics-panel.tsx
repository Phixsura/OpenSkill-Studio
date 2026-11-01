"use client";
interface DoraMetric { label: string; value: string; level: string; }
interface DoraMetricsPanelProps { metrics: DoraMetric[]; overall: string; }
const LEVEL_COLOR: Record<string, string> = { elite: "text-green-600", high: "text-blue-500", medium: "text-yellow-600", low: "text-red-500" };
export function DoraMetricsPanel({ metrics, overall }: DoraMetricsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏆 DORA Metrics</h3>
        <span className={`text-xs font-bold uppercase ${LEVEL_COLOR[overall] ?? ""}`}>{overall} performer</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4">
        {metrics.map(m => (
          <div key={m.label} className="text-center text-xs">
            <div className="text-gray-400 mb-0.5">{m.label}</div>
            <div className="font-bold text-lg">{m.value}</div>
            <div className={`text-[10px] font-bold ${LEVEL_COLOR[m.level] ?? ""}`}>{m.level}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
