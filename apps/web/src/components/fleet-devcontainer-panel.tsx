"use client";
export function FleetDevcontainerPanel({ total, running, failed, avgStartup, fast }: { total: number; running: number; failed: number; avgStartup: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 DevContainers</h3>
    <div className="text-sm">{running}/{total} running · avg {avgStartup}s startup</div>
    {fast && <span className="text-xs text-green-600">⚡ Fast startup</span>}
  </div>);
}
