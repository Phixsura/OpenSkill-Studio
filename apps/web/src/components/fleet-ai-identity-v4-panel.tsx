"use client";
export function FleetAiIdentityV4Panel({ providers, active, users, auth, mfa, zeroTrust }: { providers: number; active: number; users: number; auth: number; mfa: number; zeroTrust: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Identity v4</h3>
    <div className="text-sm">{active}/{providers} active · {users.toLocaleString()} users · {auth.toLocaleString()} auth · MFA {mfa}% · {zeroTrust ? "✅ ZT" : "⚠️"}</div>
  </div>);
}
