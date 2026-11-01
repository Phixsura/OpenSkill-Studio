"use client";
export function FleetAiPlatHealthV4Panel({ checkers, active, services, healthy, uptime, score }: { checkers: number; active: number; services: number; healthy: number; uptime: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Platform Health v4</h3>
    <div className="text-sm">{active}/{checkers} active · {healthy}/{services} healthy · {uptime}% uptime · score {score}</div>
  </div>);
}
