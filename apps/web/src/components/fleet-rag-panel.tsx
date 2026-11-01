"use client";
export function FleetRagPanel({ pipelines, active, queries, docsIndexed }: { pipelines: number; active: number; queries: number; docsIndexed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 RAG Pipelines</h3>
    <div className="text-sm">{active}/{pipelines} active · {queries.toLocaleString()} queries · {docsIndexed.toLocaleString()} docs</div>
  </div>);
}
