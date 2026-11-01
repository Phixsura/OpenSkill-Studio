"use client";
export function FleetAiMonitorV8Panel({ monitors, active, services, metrics, uptime }: { monitors: number; active: number; services: number; metrics: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Monitor v8</h3>
    <div className="text-sm">{active}/{monitors} active · {services.toLocaleString()} services · {metrics.toLocaleString()} metrics · {uptime}%</div>
  </div>);
}
