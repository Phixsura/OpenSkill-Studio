"use client";
export function FleetApiContractV9Panel({ contracts, breaking }: { contracts: number; breaking: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 API Contract v9</h3>
    <div className="text-sm">{contracts} contracts · {breaking} breaking</div>
  </div>);
}
