"use client";
export function FleetAiHealthV8Panel({ checkers, active, services, healthy, score, uptime }: { checkers: number; active: number; services: number; healthy: number; score: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health v8</h3>
    <div className="text-sm">{active}/{checkers} active · {healthy}/{services} healthy · {score}% · {uptime}% uptime</div>
  </div>);
}
