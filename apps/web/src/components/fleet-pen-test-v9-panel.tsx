"use client";
export function FleetPenTestV9Panel({ total, open }: { total: number; open: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Pen Test v9</h3>
    <div className="text-sm">{total} findings · {open} open</div>
  </div>);
}
