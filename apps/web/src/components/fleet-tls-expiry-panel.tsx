"use client";
export function FleetTlsExpiryPanel({ total, expiringSoon, expired, allValid }: { total: number; expiringSoon: number; expired: number; allValid: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Fleet TLS Certs</h3>
    {allValid ? <span className="text-xs text-green-600">✅ All {total} certs valid</span>
     : <span className="text-xs text-red-500">⚠️ {expired} expired · {expiringSoon} expiring soon</span>}
  </div>);
}
