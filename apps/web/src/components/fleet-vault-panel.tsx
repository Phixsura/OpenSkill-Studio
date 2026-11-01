"use client";
export function FleetVaultPanel({ engines, sealed, totalSecrets, healthy }: { engines: number; sealed: number; totalSecrets: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Vault</h3>
    <div className="text-sm">{engines} engines · {totalSecrets.toLocaleString()} secrets</div>
    {!healthy && <span className="text-xs text-red-500">🚨 {sealed} sealed!</span>}
  </div>);
}
