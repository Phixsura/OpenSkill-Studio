"use client";
export function FleetServiceContractV9Panel({ contracts, compliant }: { contracts: number; compliant: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Service Contract v9</h3>
    <div className="text-sm">{contracts} contracts · {compliant} compliant</div>
  </div>);
}
