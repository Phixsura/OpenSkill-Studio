"use client";
export function FleetAuth0Panel({ tenants, active, logins, mfaPct }: { tenants: number; active: number; logins: number; mfaPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Auth0</h3>
    <div className="text-sm">{active}/{tenants} active · {logins.toLocaleString()} logins · {mfaPct}% MFA</div>
  </div>);
}
