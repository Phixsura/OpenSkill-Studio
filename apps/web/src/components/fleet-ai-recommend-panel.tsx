"use client";
export function FleetAiRecommendPanel({ engines, active, requests, ctr, items }: { engines: number; active: number; requests: number; ctr: number; items: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ AI Recommendations</h3>
    <div className="text-sm">{active}/{engines} active · {requests.toLocaleString()} req · CTR {ctr}% · {items.toLocaleString()} items</div>
  </div>);
}
