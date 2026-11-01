"use client";
export function FleetServiceBudgetV9Panel({ services, overBudget }: { services: number; overBudget: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Service Budget v9</h3>
    <div className="text-sm">{services} services · {overBudget} over budget</div>
  </div>);
}
