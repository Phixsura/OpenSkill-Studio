"use client";
export function FleetLogVolPanel({ totalGb, dailyCost, sources, expensive }: { totalGb: number; dailyCost: number; sources: number; expensive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Log Volume</h3>
    <div className="text-sm">{totalGb} GB/day · ${dailyCost}/day · {sources} sources</div>
    {expensive && <span className="text-xs text-yellow-600">💸 High log costs</span>}
  </div>);
}
