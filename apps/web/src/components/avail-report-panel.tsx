"use client";
interface SvcAvail { service: string; uptimePct: number; downtimeMin: number; slaMet: boolean; }
interface AvailReportPanelProps { period: string; avgUptimePct: number; totalDowntimeMinutes: number;
  totalIncidents: number; slaBreaches: number; services: SvcAvail[]; allSlaMet: boolean; }
export function AvailReportPanel({ period, avgUptimePct, totalDowntimeMinutes, totalIncidents,
  slaBreaches, services, allSlaMet }: AvailReportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Availability Report — {period}</h3>
        <span className={`text-xs font-bold ${allSlaMet ? "text-green-600" : "text-yellow-600"}`}>
          {avgUptimePct}% avg{slaBreaches > 0 ? ` · ${slaBreaches} SLA breach` : " · ✅ All SLA met"}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2 p-3 text-center text-[11px]">
        <div><span className="text-gray-400">Downtime</span><div className="font-bold">{totalDowntimeMinutes}min</div></div>
        <div><span className="text-gray-400">Incidents</span><div className="font-bold">{totalIncidents}</div></div>
        <div><span className="text-gray-400">Breaches</span><div className={`font-bold ${slaBreaches > 0 ? "text-red-500" : ""}`}>{slaBreaches}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1 text-xs">
            <div className="flex items-center gap-1">
              <span>{s.slaMet ? "✅" : "❌"}</span>
              <span className="font-mono">{s.service}</span>
            </div>
            <span className="text-gray-400">{s.uptimePct}% · {s.downtimeMin}min down</span>
          </div>
        ))}
      </div>
    </div>
  );
}
