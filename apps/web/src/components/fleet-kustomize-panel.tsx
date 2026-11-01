"use client";
export function FleetKustomizePanel({ total, valid, invalid, stale, clean }: { total: number; valid: number; invalid: number; stale: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Kustomize</h3>
    {clean ? <span className="text-xs text-green-600">✅ All {total} overlays clean</span>
     : <span className="text-xs text-yellow-600">⚠️ {invalid} invalid · {stale} stale</span>}
  </div>);
}
