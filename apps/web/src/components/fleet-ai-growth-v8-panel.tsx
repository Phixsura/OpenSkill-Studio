"use client";
export function FleetAiGrowthV8Panel({ trackers, active, mau, arr, growth }: { trackers: number; active: number; mau: number; arr: number; growth: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Growth v8</h3>
    <div className="text-sm">{active}/{trackers} active · {mau.toLocaleString()} MAU · ${arr.toLocaleString()} ARR · +{growth}%</div>
  </div>);
}
