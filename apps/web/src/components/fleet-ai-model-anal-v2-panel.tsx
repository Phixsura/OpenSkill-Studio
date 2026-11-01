"use client";
export function FleetAiModelAnalV2Panel({ dashboards, active, models, dau, requests, revenue }: { dashboards: number; active: number; models: number; dau: number; requests: number; revenue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Model Analytics v2</h3>
    <div className="text-sm">{active}/{dashboards} active · {models} models · {dau.toLocaleString()} DAU · ${revenue.toLocaleString()}</div>
  </div>);
}
