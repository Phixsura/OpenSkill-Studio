"use client";
export function FleetSeldonPanel({ deployments, available, predictors, requests }: { deployments: number; available: number; predictors: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Seldon</h3>
    <div className="text-sm">{available}/{deployments} available · {predictors} predictors · {requests.toLocaleString()} req</div>
  </div>);
}
