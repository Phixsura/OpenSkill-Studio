"use client";
export function FleetAutoCovPanel({ total, automated, manual, coveragePct, mature }: { total: number; automated: number; manual: number; coveragePct: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Automation Coverage</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{automated} automated · {manual} manual</div>
  </div>);
}
