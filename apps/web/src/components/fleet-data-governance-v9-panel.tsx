"use client";
export function FleetDataGovernanceV9Panel({ datasets, pii }: { datasets: number; pii: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ Data Governance v9</h3>
    <div className="text-sm">{datasets} datasets · {pii} with PII</div>
  </div>);
}
