"use client";
export function FleetApiCapacityPlanningV9Panel({ apis, utilization }: { apis: number; utilization: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Capacity Planning v9</h3>
    <div className="text-sm">{apis} APIs · {utilization}% utilization</div>
  </div>);
}
