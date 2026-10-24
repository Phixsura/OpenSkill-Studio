"use client";
export function FleetContractTestV9Panel({ contracts, broken }: { contracts: number; broken: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Contract Test v9</h3>
    <div className="text-sm">{contracts} contracts · {broken} broken</div>
  </div>);
}
