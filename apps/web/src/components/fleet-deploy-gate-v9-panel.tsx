"use client";
export function FleetDeployGateV9Panel({ total, blocked }: { total: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Deploy Gate v9</h3>
    <div className="text-sm">{total} gates · {blocked} blocked</div>
  </div>);
}
