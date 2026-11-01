"use client";
export function FleetAiPrunePanel({ pruners, active, models, sparsity, accuracyDrop }: { pruners: number; active: number; models: number; sparsity: number; accuracyDrop: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✂️ AI Model Pruning</h3>
    <div className="text-sm">{active}/{pruners} active · {models} pruned · {sparsity}% sparse · -{accuracyDrop}% acc</div>
  </div>);
}
