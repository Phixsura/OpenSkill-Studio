"use client";
export function FleetAiRevenueV2Panel({ trackers, active, mrr, arr, growth, ndr }: { trackers: number; active: number; mrr: number; arr: number; growth: number; ndr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💼 AI Revenue v2</h3>
    <div className="text-sm">{active}/{trackers} active · ${mrr.toLocaleString()} MRR · ${arr.toLocaleString()} ARR · +{growth}% growth · NDR {ndr}%</div>
  </div>);
}
