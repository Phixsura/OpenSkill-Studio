"use client";
export function FleetAiMixedPrecPanel({ configs, active, speedup, memReduction, precisions }: { configs: number; active: number; speedup: number; memReduction: number; precisions: string[]; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 AI Mixed Precision</h3>
    <div className="text-sm">{active}/{configs} active · {speedup}x speed · {memReduction}% mem · {precisions.join(", ")}</div>
  </div>);
}
