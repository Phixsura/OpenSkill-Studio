"use client";

interface Resource { name: string; type: string; usagePct: number; }
interface ResMonitorPanelProps { resources: Resource[]; avgUsagePct: number;
  status: string; criticalCount: number; warningCount: number; }

export function ResMonitorPanel({ resources, avgUsagePct, status, criticalCount, warningCount }: ResMonitorPanelProps) {
  const statusLabel = status === "healthy" ? "✅ Healthy" : status === "warning" ? "⚠ Warning" : "🔴 Critical";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Resource Monitor</h3>
        <div className="flex gap-2 text-xs">
          <span>{statusLabel}</span>
          <span className="text-gray-400">avg {avgUsagePct}%</span>
        </div>
      </div>
      <div className="p-4 space-y-2.5">
        {resources.map(r => {
          const color = r.usagePct >= 90 ? "bg-red-500" : r.usagePct >= 70 ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={r.name}>
              <div className="flex justify-between text-xs mb-0.5">
                <span>{r.name} <span className="text-gray-400">({r.type})</span></span>
                <span className="font-mono">{r.usagePct}%</span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${r.usagePct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
