"use client";
export function FleetApiRatePlanV9Panel({ plans, subscribers }: { plans: number; subscribers: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 API Rate Plan v9</h3>
    <div className="text-sm">{plans} plans · {subscribers} subscribers</div>
  </div>);
}
