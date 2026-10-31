"use client";
export function FleetAiUsageAnalPanel({ dashboards, active, dau, requests, retention }: { dashboards: number; active: number; dau: number; requests: number; retention: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Usage Analytics</h3>
    <div className="text-sm">{active}/{dashboards} active · {dau.toLocaleString()} DAU · {requests.toLocaleString()} req · {retention}% retention</div>
  </div>);
}
