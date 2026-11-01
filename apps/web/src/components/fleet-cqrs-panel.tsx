"use client";
export function FleetCqrsPanel({ total, cqrsEnabled, readReplicas, adoptionPct }: { total: number; cqrsEnabled: number; readReplicas: number; adoptionPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 CQRS</h3>
    <div className="text-sm">{cqrsEnabled}/{total} CQRS ({adoptionPct}%) · {readReplicas} read replicas</div>
  </div>);
}
