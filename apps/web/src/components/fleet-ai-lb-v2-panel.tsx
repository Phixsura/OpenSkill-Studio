"use client";
export function FleetAiLbV2Panel({ balancers, active, backends, rps, algorithms }: { balancers: number; active: number; backends: number; rps: number; algorithms: string[]; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Load Balancer v2</h3>
    <div className="text-sm">{active}/{balancers} active · {backends} backends · {rps.toLocaleString()} RPS · {algorithms.join(", ")}</div>
  </div>);
}
