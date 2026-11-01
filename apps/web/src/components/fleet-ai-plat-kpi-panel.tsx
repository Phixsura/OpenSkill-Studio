"use client";
export function FleetAiPlatKpiPanel({ dashboards, active, kpis, green, red }: { dashboards: number; active: number; kpis: number; green: number; red: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Platform KPI</h3>
    <div className="text-sm">{active}/{dashboards} active · 🟢 {green} · 🔴 {red} of {kpis} KPIs</div>
  </div>);
}
