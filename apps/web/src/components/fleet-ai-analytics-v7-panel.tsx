"use client";
export function FleetAiAnalyticsV7Panel({ dashboards, active, events, insights, reports }: { dashboards: number; active: number; events: number; insights: number; reports: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Analytics v7</h3>
    <div className="text-sm">{active}/{dashboards} active · {events.toLocaleString()} events · {insights} insights · {reports} reports</div>
  </div>);
}
