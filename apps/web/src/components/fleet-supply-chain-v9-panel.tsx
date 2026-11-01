"use client";
export function FleetSupplyChainV9Panel({ artifacts, signed }: { artifacts: number; signed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Supply Chain v9</h3>
    <div className="text-sm">{artifacts} artifacts · {signed} signed</div>
  </div>);
}
