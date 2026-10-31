"use client";

interface Metric { label: string; value: number; icon: string; display?: string; trend?: string; }
interface AnalyticsOverviewProps { metrics: Metric[]; period: string; health: string; netInstalls: number; }

export function AnalyticsOverview({ metrics, period, health, netInstalls }: AnalyticsOverviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Analytics Overview</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${health === "good" ? "bg-green-500" : "bg-yellow-500"}`} />
          <span className="text-xs text-gray-400">{period}</span>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {metrics.map(m => (
          <div key={m.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <span className="text-lg">{m.icon}</span>
            <p className="text-xl font-bold mt-1">{m.display ?? m.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-center text-gray-400">
        Net installs: <span className={netInstalls >= 0 ? "text-green-600" : "text-red-600"}>{netInstalls >= 0 ? "+" : ""}{netInstalls}</span>
      </p>
    </div>
  );
}
