"use client";
export function FleetAiLbPanel({ balancers, active, rps, backends }: { balancers: number; active: number; rps: number; backends: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Load Balancer</h3>
    <div className="text-sm">{active}/{balancers} active · {rps.toLocaleString()} rps · {backends} backends</div>
  </div>);
}
