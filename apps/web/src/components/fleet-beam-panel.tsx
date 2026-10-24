"use client";
export function FleetBeamPanel({ total, running, drained, failed }: { total: number; running: number; drained: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔦 Beam</h3>
    <div className="text-sm">{running} running · {drained} drained · {failed} failed</div>
  </div>);
}
