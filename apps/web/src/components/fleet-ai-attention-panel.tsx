"use client";
export function FleetAiAttentionPanel({ analyzers, active, heads, sequences, sparsity }: { analyzers: number; active: number; heads: number; sequences: number; sparsity: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Attention</h3>
    <div className="text-sm">{active}/{analyzers} active · {heads} heads · {sequences.toLocaleString()} seq · {sparsity}% sparse</div>
  </div>);
}
