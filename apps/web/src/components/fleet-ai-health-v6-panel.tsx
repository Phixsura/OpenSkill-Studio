"use client";
export function FleetAiHealthV6Panel({ checkers, active, services, healthy, uptime }: { checkers: number; active: number; services: number; healthy: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health v6</h3>
    <div className="text-sm">{active}/{checkers} active · {healthy}/{services} healthy · {uptime}% uptime</div>
  </div>);
}
