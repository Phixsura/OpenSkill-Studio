"use client";
export function FleetActixPanel({ services, running, rps, p99 }: { services: number; running: number; rps: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦀 Actix</h3>
    <div className="text-sm">{running}/{services} running · {rps.toLocaleString()} rps · p99 {p99}ms</div>
  </div>);
}
