"use client";
export function FleetPrefectPanel({ deployments, active, completed, failed }: { deployments: number; active: number; completed: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Prefect</h3>
    <div className="text-sm">{active}/{deployments} active · {completed}✅ {failed}❌/24h</div>
  </div>);
}
