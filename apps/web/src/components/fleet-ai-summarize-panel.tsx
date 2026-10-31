"use client";
export function FleetAiSummarizePanel({ services, active, docs, compression, rougeL }: { services: number; active: number; docs: number; compression: number; rougeL: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 AI Summarization</h3>
    <div className="text-sm">{active}/{services} active · {docs.toLocaleString()} docs · {compression}x compression · ROUGE-L {rougeL}</div>
  </div>);
}
