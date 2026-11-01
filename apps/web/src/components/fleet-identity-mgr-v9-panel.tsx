"use client";
export function FleetIdentityMgrV9Panel({ total, mfa }: { total: number; mfa: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪪 Identity Manager v9</h3>
    <div className="text-sm">{total} identities · {mfa} MFA enabled</div>
  </div>);
}
