"use client";
export function FleetRollbackPanel({ total, auto, manual }: { total: number; auto: number; manual: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏪ Rollbacks</h3>
    <div className="text-sm">{total} total · {auto} auto · {manual} manual</div>
  </div>);
}
