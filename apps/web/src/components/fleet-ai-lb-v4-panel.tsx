"use client";
export function FleetAiLbV4Panel({ balancers, active, backends, rps, hc }: { balancers: number; active: number; backends: number; rps: number; hc: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Load Balancer v4</h3>
    <div className="text-sm">{active}/{balancers} active · {backends} backends · {rps.toLocaleString()} RPS · HC {hc}s</div>
  </div>);
}
