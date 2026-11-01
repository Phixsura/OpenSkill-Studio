"use client";
export function FleetZigPanel({ services, running, rps, avgMemory }: { services: number; running: number; rps: number; avgMemory: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Zig</h3>
    <div className="text-sm">{running}/{services} running · {rps.toLocaleString()} rps · {avgMemory}KB avg</div>
  </div>);
}
