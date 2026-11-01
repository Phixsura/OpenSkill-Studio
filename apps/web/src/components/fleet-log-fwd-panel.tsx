"use client";
export function FleetLogFwdPanel({ agents, healthy, bufferMb, dropped, reliable }: { agents: number; healthy: number; bufferMb: number; dropped: number; reliable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📤 Log Forwarding</h3>
    <div className="text-sm">{healthy}/{agents} agents · {bufferMb}MB buffered</div>
    {!reliable && <span className="text-xs text-yellow-600">⚠️ {dropped.toLocaleString()} events dropped</span>}
  </div>);
}
