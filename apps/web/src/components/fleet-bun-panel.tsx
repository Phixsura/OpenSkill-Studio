"use client";
export function FleetBunPanel({ apps, running, rps, avgStartup }: { apps: number; running: number; rps: number; avgStartup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐰 Bun</h3>
    <div className="text-sm">{running}/{apps} running · {rps.toLocaleString()} rps · {avgStartup}ms startup</div>
  </div>);
}
