"use client";
export function FleetAiExecDashV6Panel({ dashboards, active, revenue, cost, margin, users }: { dashboards: number; active: number; revenue: number; cost: number; margin: number; users: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👔 AI Executive Dashboard v6</h3>
    <div className="text-sm">{active}/{dashboards} active · ${revenue.toLocaleString()} rev · {margin}% margin · {users.toLocaleString()} users</div>
  </div>);
}
