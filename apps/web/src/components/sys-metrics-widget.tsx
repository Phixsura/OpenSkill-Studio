"use client";

interface SysMetricsWidgetProps { cpuPct: number; memoryPct: number;
  diskPct: number; networkMbps: number; status: string; alertCount: number; }

export function SysMetricsWidget({ cpuPct, memoryPct, diskPct, networkMbps, status, alertCount }: SysMetricsWidgetProps) {
  const metrics = [
    { label: "CPU", value: cpuPct, unit: "%" },
    { label: "Memory", value: memoryPct, unit: "%" },
    { label: "Disk", value: diskPct, unit: "%" },
    { label: "Network", value: networkMbps, unit: " Mbps" },
  ];
  const statusColor = status === "healthy" ? "text-green-600" : status === "warning" ? "text-yellow-600" : "text-red-600";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🖥️ System Metrics</h3>
        <div className="flex gap-2 text-xs">
          <span className={statusColor}>{status}</span>
          {alertCount > 0 && <span className="text-red-500">{alertCount} alerts</span>}
        </div>
      </div>
      <div className="p-4 space-y-3">
        {metrics.map(m => {
          const color = m.value > 90 ? "bg-red-500" : m.value > 70 ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={m.label}>
              <div className="flex justify-between text-xs mb-0.5">
                <span>{m.label}</span>
                <span className="font-mono">{m.value}{m.unit}</span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(m.value, 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
