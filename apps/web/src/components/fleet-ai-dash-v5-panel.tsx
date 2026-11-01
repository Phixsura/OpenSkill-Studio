"use client";
export function FleetAiDashV5Panel({ dashboards, active, widgets, users, customViews }: { dashboards: number; active: number; widgets: number; users: number; customViews: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Dashboard v5</h3>
    <div className="text-sm">{active}/{dashboards} active · {widgets} widgets · {users.toLocaleString()} users · {customViews} custom views</div>
  </div>);
}
