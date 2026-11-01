"use client";
export function FleetAiPlatMonV3Panel({ monitors, active, services, metrics, dashboards, alerts }: { monitors: number; active: number; services: number; metrics: number; dashboards: number; alerts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Monitoring v3</h3>
    <div className="text-sm">{active}/{monitors} active · {services} services · {metrics.toLocaleString()} metrics · {dashboards} dashboards · {alerts} alerts</div>
  </div>);
}
