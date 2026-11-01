"use client";
export function FleetNomadPanel({ total, running, dead, pending }: { total: number; running: number; dead: number; pending: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏃 Nomad</h3>
    <div className="text-sm">{running} running · {dead} dead · {pending} pending</div>
  </div>);
}
