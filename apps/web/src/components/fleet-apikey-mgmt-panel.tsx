"use client";
export function FleetApikeyMgmtPanel({ total, active, expired, expiringSoon, needsRotation }: { total: number; active: number; expired: number; expiringSoon: number; needsRotation: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 API Keys</h3>
    <div className="text-sm">{active} active · {expired} expired</div>
    {needsRotation && <span className="text-xs text-yellow-600">⚠️ {expiringSoon} expiring soon</span>}
  </div>);
}
