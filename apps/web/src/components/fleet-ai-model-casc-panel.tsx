"use client";
export function FleetAiModelCascPanel({ cascades, active, requests, avgDepth, saved }: { cascades: number; active: number; requests: number; avgDepth: number; saved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Model Cascade</h3>
    <div className="text-sm">{active}/{cascades} active · {requests.toLocaleString()} req · depth {avgDepth} · {saved}% cost saved</div>
  </div>);
}
