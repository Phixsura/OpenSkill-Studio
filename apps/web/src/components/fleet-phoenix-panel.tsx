"use client";
export function FleetPhoenixPanel({ apps, running, channels, wsConnections }: { apps: number; running: number; channels: number; wsConnections: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 Phoenix</h3>
    <div className="text-sm">{running}/{apps} running · {channels} channels · {wsConnections.toLocaleString()} WS</div>
  </div>);
}
