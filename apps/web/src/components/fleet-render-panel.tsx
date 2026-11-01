"use client";
export function FleetRenderPanel({ services, running, suspended }: { services: number; running: number; suspended: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎨 Render</h3>
    <div className="text-sm">{running}/{services} running</div>
    {suspended > 0 && <span className="text-xs text-yellow-600">⏸️ {suspended} suspended</span>}
  </div>);
}
