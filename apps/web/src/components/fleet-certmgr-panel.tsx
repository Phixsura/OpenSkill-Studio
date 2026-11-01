"use client";
export function FleetCertmgrPanel({ total, ready, expiring, failedRenewal, healthy }: { total: number; ready: number; expiring: number; failedRenewal: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 cert-manager</h3>
    <div className="text-sm">{ready}/{total} ready</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {expiring} expiring · {failedRenewal} failed</span>}
  </div>);
}
