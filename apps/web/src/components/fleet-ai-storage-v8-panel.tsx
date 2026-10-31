"use client";
export function FleetAiStorageV8Panel({ systems, active, totalEb, iops, durability }: { systems: number; active: number; totalEb: number; iops: number; durability: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Storage v8</h3>
    <div className="text-sm">{active}/{systems} active · {totalEb}EB · {iops.toLocaleString()} IOPS · {durability}% durability</div>
  </div>);
}
