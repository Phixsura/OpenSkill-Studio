"use client";
export function FleetConsumerLagPanel({ groups, totalLag, maxLag, behind, caughtUp }: { groups: number; totalLag: number; maxLag: number; behind: number; caughtUp: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 Consumer Lag</h3>
    <div className="text-sm">{totalLag.toLocaleString()} total · max {maxLag.toLocaleString()}</div>
    {!caughtUp && <span className="text-xs text-yellow-600">⚠️ {behind} groups behind</span>}
  </div>);
}
