"use client";
export function FleetAiSearchPanel({ engines, active, queries, relevance }: { engines: number; active: number; queries: number; relevance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Search</h3>
    <div className="text-sm">{active}/{engines} active · {queries.toLocaleString()} queries · {relevance}% relevance</div>
  </div>);
}
