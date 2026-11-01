"use client";
export function FleetAiSemSearchPanel({ engines, active, queries, docs, mrr }: { engines: number; active: number; queries: number; docs: number; mrr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Semantic Search</h3>
    <div className="text-sm">{active}/{engines} active · {queries.toLocaleString()} queries · {docs.toLocaleString()} docs · MRR {mrr}</div>
  </div>);
}
