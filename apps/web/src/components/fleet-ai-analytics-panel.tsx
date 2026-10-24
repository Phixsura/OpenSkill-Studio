"use client";
export function FleetAiAnalyticsPanel({ dashboards, active, metrics, views }: { dashboards: number; active: number; metrics: number; views: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Analytics</h3>
    <div className="text-sm">{active}/{dashboards} active · {metrics} metrics · {views.toLocaleString()} views</div>
  </div>);
}
