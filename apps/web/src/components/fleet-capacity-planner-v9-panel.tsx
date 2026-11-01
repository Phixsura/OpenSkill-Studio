"use client";
export function FleetCapacityPlannerV9Panel({ utilization, resources }: { utilization: number; resources: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Capacity Planner v9</h3>
    <div className="text-sm">{resources} resources · {utilization}% utilized</div>
  </div>);
}
