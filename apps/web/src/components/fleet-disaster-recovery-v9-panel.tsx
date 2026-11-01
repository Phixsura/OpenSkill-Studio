"use client";
export function FleetDisasterRecoveryV9Panel({ plans, tested }: { plans: number; tested: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 Disaster Recovery v9</h3>
    <div className="text-sm">{plans} plans · {tested} tested</div>
  </div>);
}
