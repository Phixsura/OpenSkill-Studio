"use client";
export function FleetUptimeSlaPanel({ uptimePct, downtimeMin, nines, meetsSla }: { uptimePct: number; downtimeMin: number; nines: number; meetsSla: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Uptime SLA</h3>
    <div className={`text-lg font-bold ${meetsSla ? "text-green-600" : "text-red-500"}`}>{uptimePct}%</div>
    <div className="text-xs text-gray-400">{downtimeMin}min downtime · {nines} nines</div>
  </div>);
}
