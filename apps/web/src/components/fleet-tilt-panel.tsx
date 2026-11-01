"use client";
export function FleetTiltPanel({ total, running, resources, avgUpdate, fast }: { total: number; running: number; resources: number; avgUpdate: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Tilt</h3>
    <div className="text-sm">{running}/{total} running · {resources} resources · {avgUpdate}ms</div>
    {fast && <span className="text-xs text-green-600">⚡ Fast updates</span>}
  </div>);
}
