"use client";
export function FleetSloBudgetV9Panel({ slos, avgBudget }: { slos: number; avgBudget: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 SLO Budget v9</h3>
    <div className="text-sm">{slos} SLOs · {avgBudget}% budget remaining</div>
  </div>);
}
