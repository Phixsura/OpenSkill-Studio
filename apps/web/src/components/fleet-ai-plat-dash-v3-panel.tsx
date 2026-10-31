"use client";
export function FleetAiPlatDashV3Panel({ dashboards, active, widgets, users, realTime }: { dashboards: number; active: number; widgets: number; users: number; realTime: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Platform Dashboard v3</h3>
    <div className="text-sm">{active}/{dashboards} active · {widgets} widgets · {users.toLocaleString()} users · {realTime ? "🟢 live" : "⚪ batch"}</div>
  </div>);
}
