"use client";
export function FleetAiTokOptPanel({ optimizers, active, optimized, tokensSaved, savings }: { optimizers: number; active: number; optimized: number; tokensSaved: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✂️ AI Token Optimizer</h3>
    <div className="text-sm">{active}/{optimizers} active · {optimized.toLocaleString()} optimized · {tokensSaved.toLocaleString()} saved · {savings}%</div>
  </div>);
}
