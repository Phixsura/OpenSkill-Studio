"use client";
export function FleetFalcoPanel({ nodes, active, alerts, critical, clean }: { nodes: number; active: number; alerts: number; critical: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦅 Falco</h3>
    <div className="text-sm">{active}/{nodes} active · {alerts} alerts/24h</div>
    {!clean && <span className="text-xs text-red-500">🚨 {critical} critical alerts!</span>}
  </div>);
}
