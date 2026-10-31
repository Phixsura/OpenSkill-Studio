"use client";
export function FleetOauthPanel({ issued, active, revoked, revocationRate }: { issued: number; active: number; revoked: number; revocationRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎫 OAuth Tokens</h3>
    <div className="text-sm">{active.toLocaleString()} active · {issued.toLocaleString()} issued · {revocationRate}% revoked</div>
  </div>);
}
