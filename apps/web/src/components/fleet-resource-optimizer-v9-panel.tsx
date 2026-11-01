"use client";
export function FleetResourceOptimizerV9Panel({ recs, savings }: { recs: number; savings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Resource Optimizer v9</h3>
    <div className="text-sm">{recs} recs · ${savings.toLocaleString()}/mo saved</div>
  </div>);
}
