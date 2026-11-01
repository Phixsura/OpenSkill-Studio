"use client";
export function FleetErrorBudgetV9Panel({ slos, remaining }: { slos: number; remaining: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Error Budget v9</h3>
    <div className="text-sm">{slos} SLOs · {remaining}% remaining</div>
  </div>);
}
