"use client";
export function FleetSaltPanel({ total, connected, disconnected }: { total: number; connected: number; disconnected: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧂 SaltStack</h3>
    <div className="text-sm">{connected}/{total} connected</div>
    {disconnected > 0 && <span className="text-xs text-red-500">⚠️ {disconnected} disconnected</span>}
  </div>);
}
