"use client";

interface DoraMetric { value: number; level: string; }
interface DoraMetricsDashProps { deployFrequency: DoraMetric; leadTime: DoraMetric;
  mttr: DoraMetric; changeFailureRate: DoraMetric; overall: string; }

const LEVEL_COLORS: Record<string, string> = {
  elite: "text-green-600", high: "text-blue-600", medium: "text-yellow-600", low: "text-red-600",
};

export function DoraMetricsDash({ deployFrequency, leadTime, mttr, changeFailureRate, overall }: DoraMetricsDashProps) {
  const metrics = [
    { name: "Deploy Frequency", ...deployFrequency, unit: "/day" },
    { name: "Lead Time", ...leadTime, unit: "h" },
    { name: "MTTR", ...mttr, unit: "h" },
    { name: "Change Failure", ...changeFailureRate, unit: "%" },
  ];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 DORA Metrics</h3>
        <span className={`text-sm font-bold ${LEVEL_COLORS[overall] ?? ""}`}>{overall}</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {metrics.map(m => (
          <div key={m.name} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{m.value}{m.unit}</div>
            <div className="text-[9px] text-gray-400">{m.name}</div>
            <div className={`text-[10px] font-medium ${LEVEL_COLORS[m.level] ?? ""}`}>{m.level}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
