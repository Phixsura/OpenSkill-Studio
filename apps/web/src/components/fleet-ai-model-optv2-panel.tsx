"use client";
export function FleetAiModelOptv2Panel({ optimizers, active, models, speedup, memReduction }: { optimizers: number; active: number; models: number; speedup: number; memReduction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Model Optimizer v2</h3>
    <div className="text-sm">{active}/{optimizers} active · {models} models · {speedup}x speed · {memReduction}% mem saved</div>
  </div>);
}
