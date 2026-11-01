"use client";
export function FleetAiGrowthV6Panel({ trackers, active, mau, arr, growth, ndr }: { trackers: number; active: number; mau: number; arr: number; growth: number; ndr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Growth v6</h3>
    <div className="text-sm">{active}/{trackers} active · {mau.toLocaleString()} MAU · ${arr.toLocaleString()} ARR · +{growth}% · NDR {ndr}%</div>
  </div>);
}
