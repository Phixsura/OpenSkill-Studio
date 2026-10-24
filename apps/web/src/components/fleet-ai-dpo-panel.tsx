"use client";
export function FleetAiDpoPanel({ trainers, active, pairs, epochs, winRate }: { trainers: number; active: number; pairs: number; epochs: number; winRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI DPO Training</h3>
    <div className="text-sm">{active}/{trainers} active · {pairs.toLocaleString()} pairs · {epochs} epochs · {winRate}% win rate</div>
  </div>);
}
