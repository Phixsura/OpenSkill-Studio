"use client";
export function FleetAiReqDedupPanel({ dedupers, active, requests, deduped, savings }: { dedupers: number; active: number; requests: number; deduped: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Request Dedup</h3>
    <div className="text-sm">{active}/{dedupers} active · {requests.toLocaleString()} req · {deduped.toLocaleString()} deduped · {savings}% saved</div>
  </div>);
}
