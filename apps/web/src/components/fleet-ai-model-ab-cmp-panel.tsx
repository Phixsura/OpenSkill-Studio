"use client";
export function FleetAiModelAbCmpPanel({ comparators, active, comparisons, winners, ties }: { comparators: number; active: number; comparisons: number; winners: number; ties: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 AI Model A/B Compare</h3>
    <div className="text-sm">{active}/{comparators} active · {comparisons.toLocaleString()} comparisons · {winners.toLocaleString()} winners · {ties.toLocaleString()} ties</div>
  </div>);
}
