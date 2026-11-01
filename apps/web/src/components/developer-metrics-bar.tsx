"use client";

interface Metric { key: string; label: string; value: number; icon: string; format: string; }
interface DeveloperMetricsBarProps { metrics: Metric[]; period: string; }

export function DeveloperMetricsBar({ metrics, period }: DeveloperMetricsBarProps) {
  const formatValue = (m: Metric) => {
    if (m.format === "currency") return `$${(m.value / 100).toFixed(2)}`;
    if (m.format === "rating") return `${m.value.toFixed(1)} ★`;
    return m.value.toLocaleString();
  };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-500">Overview</h3>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{period}</span>
      </div>
      <div className="mt-3 grid grid-cols-5 gap-4">
        {metrics.map(m => (
          <div key={m.key} className="text-center">
            <span className="text-lg">{m.icon}</span>
            <p className="mt-1 text-xl font-bold">{formatValue(m)}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
