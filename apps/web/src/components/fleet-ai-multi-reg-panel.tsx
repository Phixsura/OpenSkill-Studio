"use client";
export function FleetAiMultiRegPanel({ deployments, active, regions, rps, failoverOk }: { deployments: number; active: number; regions: number; rps: number; failoverOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Multi-Region</h3>
    <div className="text-sm">{active}/{deployments} active · {regions} regions · {rps.toLocaleString()} RPS · {failoverOk ? "✅" : "⚠️"} failover</div>
  </div>);
}
