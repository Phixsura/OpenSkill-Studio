"use client";
export function FleetOpaPanel({ policies, totalEval, denied, avgLatency }: { policies: number; totalEval: number; denied: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 OPA Policies</h3>
    <div className="text-sm">{policies} policies · {totalEval.toLocaleString()} evals · {denied} denied · {avgLatency}ms</div>
  </div>);
}
