"use client";
export function FleetIrtPanel({ total, avgAck, withinSla, slaPct }: { total: number; avgAck: number; withinSla: number; slaPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Response</h3>
    <div className="text-sm">avg {avgAck}min · {withinSla}/{total} within SLA ({slaPct}%)</div>
  </div>);
}
