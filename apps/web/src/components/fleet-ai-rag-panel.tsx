"use client";
export function FleetAiRagPanel({ pipelines, active, queries, docs, relevance }: { pipelines: number; active: number; queries: number; docs: number; relevance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 AI RAG Pipeline</h3>
    <div className="text-sm">{active}/{pipelines} active · {queries.toLocaleString()} queries · {docs.toLocaleString()} docs · {(relevance * 100).toFixed(0)}% relevance</div>
  </div>);
}
