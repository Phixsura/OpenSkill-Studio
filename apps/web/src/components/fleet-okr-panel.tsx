"use client";
export function FleetOkrPanel({ total, onTrack, atRisk, behind, avgProgress }: { total: number; onTrack: number; atRisk: number; behind: number; avgProgress: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 OKRs</h3>
    <div className="text-sm">🟢 {onTrack} · 🟡 {atRisk} · 🔴 {behind} · avg {avgProgress}%</div>
  </div>);
}
