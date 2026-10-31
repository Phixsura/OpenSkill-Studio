"use client";

interface UptimeInfo { service: string; uptimePct: number; currentStreak: number; sla99: boolean; sla999: boolean; sla9999: boolean; }

export function UptimeMonitorPanel({ services, overallUptime }: {
  services: UptimeInfo[]; overallUptime: number;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⏱️ Uptime Monitor</h2>
        <span className={`text-xl font-bold ${overallUptime >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>
          {overallUptime}%
        </span>
      </div>
      <div className="space-y-1">
        {services.map((s) => (
          <div key={s.service} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${s.currentStreak > 0 ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-semibold text-sm">{s.service}</span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className={`font-bold ${s.uptimePct >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{s.uptimePct}%</span>
              <span className="text-gray-400">streak: {s.currentStreak}</span>
              {s.sla9999 && <span className="bg-green-100 text-green-700 px-1.5 py-0.5 rounded">99.99%</span>}
              {!s.sla9999 && s.sla999 && <span className="bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">99.9%</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
