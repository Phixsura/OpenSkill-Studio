"use client";
export function FleetAiLivenessPanel({ checkers, active, services, alive, restarts }: { checkers: number; active: number; services: number; alive: number; restarts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💓 AI Liveness</h3>
    <div className="text-sm">{active}/{checkers} active · {alive}/{services} alive · {restarts} restarts</div>
  </div>);
}
