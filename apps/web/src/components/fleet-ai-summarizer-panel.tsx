"use client";
export function FleetAiSummarizerPanel({ services, active, docs, avgCompression }: { services: number; active: number; docs: number; avgCompression: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Summarizer</h3>
    <div className="text-sm">{active}/{services} active · {docs.toLocaleString()} docs · {avgCompression}x compression</div>
  </div>);
}
