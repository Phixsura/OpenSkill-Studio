"use client";
export function FleetAiHybridSrchPanel({ engines, active, queries, mrr, docs }: { engines: number; active: number; queries: number; mrr: number; docs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Hybrid Search</h3>
    <div className="text-sm">{active}/{engines} active · {queries.toLocaleString()} queries · MRR {mrr} · {docs.toLocaleString()} docs</div>
  </div>);
}
