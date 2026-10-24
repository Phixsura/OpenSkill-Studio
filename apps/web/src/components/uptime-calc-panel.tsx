"use client";
interface UptimeCalcPanelProps { uptimePct: number; nines: number; downtimeMinutes: number;
  incidents: number; slaLabel: string; }
export function UptimeCalcPanel({ uptimePct, nines, downtimeMinutes, incidents, slaLabel }: UptimeCalcPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Uptime</h3>
        <span className={`text-xs font-bold ${nines >= 3 ? "text-green-600" : "text-yellow-600"}`}>
          {uptimePct}% · {slaLabel}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Uptime</span><div className="font-bold text-lg text-green-600">{uptimePct}%</div></div>
        <div><span className="text-gray-400">Downtime</span><div className="font-bold text-lg">{downtimeMinutes}min</div></div>
        <div><span className="text-gray-400">Incidents</span><div className="font-bold text-lg">{incidents}</div></div>
      </div>
    </div>
  );
}
