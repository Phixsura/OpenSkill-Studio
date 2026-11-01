"use client";
interface IncidentTimerPanelProps { avgAckMinutes: number; avgResolveMinutes: number;
  ackSlaPct: number; totalIncidents: number; slaMet: number; }
export function IncidentTimerPanel({ avgAckMinutes, avgResolveMinutes, ackSlaPct, totalIncidents, slaMet }: IncidentTimerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Incident Response</h3>
        <span className={`text-xs font-bold ${ackSlaPct >= 90 ? "text-green-600" : "text-yellow-600"}`}>
          {ackSlaPct}% SLA met · {totalIncidents} incidents
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Avg Ack</span><div className="font-bold text-lg">{avgAckMinutes}min</div></div>
        <div><span className="text-gray-400">Avg Resolve</span><div className="font-bold text-lg">{avgResolveMinutes}min</div></div>
        <div><span className="text-gray-400">SLA Met</span><div className="font-bold text-lg">{slaMet}/{totalIncidents}</div></div>
      </div>
    </div>
  );
}
