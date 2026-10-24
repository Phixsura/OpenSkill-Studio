"use client";
export function FleetSealedSecPanel({ total, sealed, unsealed, expiredKeys, secure }: { total: number; sealed: number; unsealed: number; expiredKeys: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Sealed Secrets</h3>
    <div className="text-sm">{sealed}/{total} sealed</div>
    {!secure && <span className="text-xs text-red-500">⚠️ {unsealed} unsealed · {expiredKeys} expired keys</span>}
  </div>);
}
