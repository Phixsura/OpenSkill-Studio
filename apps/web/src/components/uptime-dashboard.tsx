"use client";

interface UptimeMonitor { name: string; uptimePct: number; slaMet: boolean;
  totalChecks: number; downPeriods: number; }
interface UptimeDashboardProps { monitors: UptimeMonitor[]; avgUptime: number; allSlaMet: boolean; }

export function UptimeDashboard({ monitors, avgUptime, allSlaMet }: UptimeDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Uptime Monitor</h3>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${avgUptime >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{avgUptime}%</span>
          <span className={`text-xs ${allSlaMet ? "text-green-600" : "text-yellow-600"}`}>
            {allSlaMet ? "✅ SLA Met" : "⚠ SLA Issues"}
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {monitors.map(m => (
          <div key={m.name} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{m.name}</span>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-mono ${m.uptimePct >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{m.uptimePct}%</span>
                <span className="text-[10px] text-gray-400">{m.downPeriods} incidents</span>
              </div>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${m.uptimePct >= 99.9 ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${m.uptimePct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
