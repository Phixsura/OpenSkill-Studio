"use client";
export function FleetAbResultPanel({ total, winners, losers, inconclusive, winRate }: { total: number; winners: number; losers: number; inconclusive: number; winRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 A/B Results</h3>
    <div className="text-sm">🏆 {winners} · ❌ {losers} · 🤷 {inconclusive} ({winRate}% win rate)</div>
  </div>);
}
