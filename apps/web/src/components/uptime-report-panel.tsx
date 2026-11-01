"use client";
interface SvcUptime { service: string; uptimePct: number; incidents: number; downtimeMinutes: number; slaMet: boolean; }
interface UptimeReportPanelProps { period: string; services: SvcUptime[]; avgUptimePct: number; allSlaMet: boolean; }
export function UptimeReportPanel({ period, services, avgUptimePct, allSlaMet }: UptimeReportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Uptime Report — {period}</h3>
        <span className={`text-xs font-bold ${allSlaMet ? "text-green-600" : "text-yellow-600"}`}>
          avg {avgUptimePct}%{allSlaMet ? " · ✅ All SLA met" : " · ⚠ SLA breached"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={s.slaMet ? "text-green-600" : "text-red-500"}>{s.slaMet ? "✅" : "❌"}</span>
              <span className="font-mono">{s.service}</span>
            </div>
            <span className="text-gray-400">{s.uptimePct}% · {s.incidents} incidents · {s.downtimeMinutes}min down</span>
          </div>
        ))}
      </div>
    </div>
  );
}
