"use client";
export function FleetAiPlatAnalPanel({ dashboards, active, dau, mau, apiCalls, revenue }: { dashboards: number; active: number; dau: number; mau: number; apiCalls: number; revenue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Platform Analytics</h3>
    <div className="text-sm">{active}/{dashboards} active · {dau.toLocaleString()} DAU · {mau.toLocaleString()} MAU · ${revenue.toLocaleString()}</div>
  </div>);
}
