"use client";
export function FleetAiRevenueV8Panel({ trackers, active, mrr, ndr, margin }: { trackers: number; active: number; mrr: number; ndr: number; margin: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Revenue v8</h3>
    <div className="text-sm">{active}/{trackers} active · ${mrr.toLocaleString()} MRR · NDR {ndr}% · margin {margin}%</div>
  </div>);
}
