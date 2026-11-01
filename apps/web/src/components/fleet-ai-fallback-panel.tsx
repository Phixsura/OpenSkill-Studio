"use client";
export function FleetAiFallbackPanel({ chains, active, fallbacks, primarySuccess }: { chains: number; active: number; fallbacks: number; primarySuccess: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Fallback</h3>
    <div className="text-sm">{active}/{chains} active · {fallbacks} fallbacks · {primarySuccess}% primary success</div>
  </div>);
}
