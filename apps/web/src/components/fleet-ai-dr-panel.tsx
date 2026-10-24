"use client";
export function FleetAiDrPanel({ plans, active, rto, rpo, lastDrill }: { plans: number; active: number; rto: number; rpo: number; lastDrill: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Disaster Recovery</h3>
    <div className="text-sm">{active}/{plans} active · RTO {rto}m · RPO {rpo}m · last drill {lastDrill}d ago</div>
  </div>);
}
