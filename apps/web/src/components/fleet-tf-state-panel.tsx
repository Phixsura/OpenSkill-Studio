"use client";
export function FleetTfStatePanel({ total, healthy, locked, failed, allOk }: { total: number; healthy: number; locked: number; failed: number; allOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Terraform State</h3>
    <div className="text-sm">{healthy}/{total} healthy</div>
    {!allOk && <span className="text-xs text-yellow-600">⚠️ {locked} locked · {failed} failed</span>}
  </div>);
}
