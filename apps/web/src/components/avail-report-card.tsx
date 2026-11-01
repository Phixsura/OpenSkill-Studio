"use client";

interface ServiceAvail { name: string; uptimePct: number; downtimeMin: number;
  slaTarget: number; slaMet: boolean; incidents: number; }
interface AvailReportCardProps { services: ServiceAvail[]; avgUptime: number;
  slaBreaches: number; allSlaMet: boolean; periodDays: number; }

export function AvailReportCard({ services, avgUptime, slaBreaches, allSlaMet, periodDays }: AvailReportCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Availability ({periodDays}d)</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{avgUptime}%</span>
          <span className={allSlaMet ? "text-green-600" : "text-red-500"}>
            {allSlaMet ? "✅ All SLA Met" : `⚠ ${slaBreaches} breaches`}
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-0.5">
              <span className="text-sm font-medium">{s.slaMet ? "🟢" : "🔴"} {s.name}</span>
              <span className="text-xs font-mono">{s.uptimePct}% / {s.slaTarget}%</span>
            </div>
            <div className="text-[10px] text-gray-400">{s.downtimeMin}min downtime · {s.incidents} incidents</div>
          </div>
        ))}
      </div>
    </div>
  );
}
