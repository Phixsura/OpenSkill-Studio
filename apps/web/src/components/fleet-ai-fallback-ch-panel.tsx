"use client";
export function FleetAiFallbackChPanel({ chains, active, fallbacks, models, successRate }: { chains: number; active: number; fallbacks: number; models: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Fallback Chain</h3>
    <div className="text-sm">{active}/{chains} active · {fallbacks.toLocaleString()} fallbacks · {models} models · {successRate}% success</div>
  </div>);
}
