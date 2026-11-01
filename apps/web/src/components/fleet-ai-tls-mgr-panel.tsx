"use client";
export function FleetAiTlsMgrPanel({ managers, active, certs, expiring, autoRenewed }: { managers: number; active: number; certs: number; expiring: number; autoRenewed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI TLS Manager</h3>
    <div className="text-sm">{active}/{managers} active · {certs} certs · {expiring} expiring · {autoRenewed} auto-renewed</div>
  </div>);
}
