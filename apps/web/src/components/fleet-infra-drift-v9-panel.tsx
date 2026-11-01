"use client";
export function FleetInfraDriftV9Panel({ stacks, drifted }: { stacks: number; drifted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Infra Drift v9</h3>
    <div className="text-sm">{stacks} stacks · {drifted} drifted</div>
  </div>);
}
