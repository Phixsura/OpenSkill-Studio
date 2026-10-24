"use client";

interface Metric { label: string; value: string | number; icon: string; }
interface AppStatsCardGridProps { metrics: Metric[]; }

export function AppStatsCardGrid({ metrics }: AppStatsCardGridProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {metrics.map(m => (
        <div key={m.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <span className="text-xl">{m.icon}</span>
          <p className="text-lg font-bold">{typeof m.value === "number" ? m.value.toLocaleString() : m.value}</p>
          <p className="text-xs text-gray-500">{m.label}</p>
        </div>
      ))}
    </div>
  );
}
