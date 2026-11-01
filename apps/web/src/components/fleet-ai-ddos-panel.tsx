"use client";
export function FleetAiDdosPanel({ systems, active, attacks, peakGbps, uptime }: { systems: number; active: number; attacks: number; peakGbps: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI DDoS Protection</h3>
    <div className="text-sm">{active}/{systems} active · {attacks} attacks · {peakGbps} Gbps peak · {uptime}% uptime</div>
  </div>);
}
