"use client";
export function FleetAiSlaMgrPanel({ slas, active, met, breached, uptime }: { slas: number; active: number; met: number; breached: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI SLA Manager</h3>
    <div className="text-sm">{active}/{slas} active · {met} met · {breached} breached · {uptime}% uptime</div>
  </div>);
}
