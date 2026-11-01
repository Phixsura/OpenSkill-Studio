"use client";
interface SvcLevelRptPanelProps { period: string; compliancePct: number; sloMet: number;
  sloBreached: number; avgUptimePct: number; totalIncidents: number;
  totalDowntimeMin: number; executiveSummary: string; }
export function SvcLevelRptPanel({ period, compliancePct, sloMet, sloBreached, avgUptimePct,
  totalIncidents, totalDowntimeMin, executiveSummary }: SvcLevelRptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${sloBreached === 0 ? "bg-green-500" : "bg-yellow-500"}`}>
        <h2 className="font-bold text-lg">Service Level Report — {period}</h2>
        <p className="text-sm opacity-80">{executiveSummary} · {compliancePct}% compliance</p>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">SLO Met</span><div className="font-bold text-green-600 text-lg">{sloMet}</div></div>
        <div><span className="text-gray-400">Breached</span><div className={`font-bold text-lg ${sloBreached > 0 ? "text-red-500" : ""}`}>{sloBreached}</div></div>
        <div><span className="text-gray-400">Uptime</span><div className="font-bold text-lg">{avgUptimePct}%</div></div>
        <div><span className="text-gray-400">Incidents</span><div className="font-bold text-lg">{totalIncidents}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 p-3 text-center text-xs text-gray-400">
        Total downtime: {totalDowntimeMin} minutes
      </div>
    </div>
  );
}
