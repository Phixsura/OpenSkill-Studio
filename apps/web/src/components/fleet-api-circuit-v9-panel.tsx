"use client";
export function FleetApiCircuitV9Panel({ circuits, open }: { circuits: number; open: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ API Circuit v9</h3>
    <div className="text-sm">{circuits} circuits · {open} open</div>
  </div>);
}
