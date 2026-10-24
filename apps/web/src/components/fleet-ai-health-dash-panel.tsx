"use client";
export function FleetAiHealthDashPanel({ dashboards, active, services, healthy, alerts, healthPct }: { dashboards: number; active: number; services: number; healthy: number; alerts: number; healthPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health Dashboard</h3>
    <div className="text-sm">{active}/{dashboards} active · {healthy}/{services} healthy · {alerts} alerts · {healthPct}%</div>
  </div>);
}
