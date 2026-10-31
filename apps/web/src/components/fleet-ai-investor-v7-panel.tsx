"use client";
export function FleetAiInvestorV7Panel({ trackers, active, arr, growth, ndr, rule40 }: { trackers: number; active: number; arr: number; growth: number; ndr: number; rule40: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💼 AI Investor v7</h3>
    <div className="text-sm">{active}/{trackers} active · ${arr.toLocaleString()} ARR · +{growth}% · NDR {ndr}% · Rule of 40: {rule40}</div>
  </div>);
}
