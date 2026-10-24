"use client";
export function FleetWebsocketPanel({ connections, maxConnections, utilPct, errorsPerMin, healthy }: { connections: number; maxConnections: number; utilPct: number; errorsPerMin: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 WebSocket</h3>
    <div className="text-sm">{connections.toLocaleString()}/{maxConnections.toLocaleString()} ({utilPct}%)</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {errorsPerMin} errors/min</span>}
  </div>);
}
