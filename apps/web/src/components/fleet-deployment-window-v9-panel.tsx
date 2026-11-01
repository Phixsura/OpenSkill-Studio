"use client";
export function FleetDeploymentWindowV9Panel({ windows, open }: { windows: number; open: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪟 Deploy Window v9</h3>
    <div className="text-sm">{windows} windows · {open} open</div>
  </div>);
}
