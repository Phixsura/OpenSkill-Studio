"use client";
export function FleetAiDdosV8Panel({ systems, active, attacks, peak, uptime }: { systems: number; active: number; attacks: number; peak: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI DDoS v8</h3>
    <div className="text-sm">{active}/{systems} active · {attacks} attacks · {peak}Tbps peak · {uptime}%</div>
  </div>);
}
