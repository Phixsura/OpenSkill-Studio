"use client";
export function FleetAiDashBuildPanel({ builders, active, dashboards, panels, viewers }: { builders: number; active: number; dashboards: number; panels: number; viewers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Dashboard Builder</h3>
    <div className="text-sm">{active}/{builders} active · {dashboards} dashboards · {panels.toLocaleString()} panels · {viewers.toLocaleString()} viewers</div>
  </div>);
}
