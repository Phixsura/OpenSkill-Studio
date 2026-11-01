"use client";
export function FleetAiNetBwPanel({ monitors, active, ingress, egress, utilization }: { monitors: number; active: number; ingress: number; egress: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Network Bandwidth</h3>
    <div className="text-sm">{active}/{monitors} active · ↓{ingress}Gbps · ↑{egress}Gbps · {utilization}% util</div>
  </div>);
}
