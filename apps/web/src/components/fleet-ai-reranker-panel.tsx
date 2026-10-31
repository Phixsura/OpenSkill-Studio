"use client";
export function FleetAiRerankerPanel({ rerankers, active, queries, ndcgBoost, latency }: { rerankers: number; active: number; queries: number; ndcgBoost: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Reranker</h3>
    <div className="text-sm">{active}/{rerankers} active · {queries.toLocaleString()} queries · +{ndcgBoost} NDCG · {latency}ms</div>
  </div>);
}
