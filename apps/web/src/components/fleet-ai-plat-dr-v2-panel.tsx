"use client";
export function FleetAiPlatDrV2Panel({ plans, active, rto, rpo, drills, regions }: { plans: number; active: number; rto: number; rpo: number; drills: number; regions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI DR v2</h3>
    <div className="text-sm">{active}/{plans} active · RTO {rto}m · RPO {rpo}m · {drills} drills · {regions} regions</div>
  </div>);
}
