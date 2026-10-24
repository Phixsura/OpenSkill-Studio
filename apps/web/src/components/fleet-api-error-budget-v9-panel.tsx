"use client";
export function FleetApiErrorBudgetV9Panel({ apis, remaining }: { apis: number; remaining: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 API Error Budget v9</h3>
    <div className="text-sm">{apis} APIs · {remaining}% budget remaining</div>
  </div>);
}
