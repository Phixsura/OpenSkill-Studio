"use client";
export function FleetDeprecationPanel({ total, deprecated, stillUsed, safeToRemove }: { total: number; deprecated: number; stillUsed: number; safeToRemove: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚠️ API Deprecation</h3>
    <div className="text-sm">{deprecated} deprecated · {stillUsed} still used · {safeToRemove} removable</div>
  </div>);
}
