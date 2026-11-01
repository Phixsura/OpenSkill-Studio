"use client";
export function FleetAiInfOptV2Panel({ optimizers, active, models, speedup, techniques }: { optimizers: number; active: number; models: number; speedup: number; techniques: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Inference Optimizer v2</h3>
    <div className="text-sm">{active}/{optimizers} active · {models} models · {speedup}x speed · {techniques} techniques</div>
  </div>);
}
