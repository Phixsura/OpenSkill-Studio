"use client";
export function FleetEncryptionPanel({ total, both, fullyEncrypted }: { total: number; both: number; fullyEncrypted: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Encryption</h3>
    {fullyEncrypted ? <span className="text-xs text-green-600">✅ All {total} fully encrypted</span>
     : <span className="text-xs text-yellow-600">⚠️ {both}/{total} fully encrypted</span>}
  </div>);
}
