"use client";
export function FleetAiIdentityV8Panel({ providers, active, users, auth, mfa, zt }: { providers: number; active: number; users: number; auth: number; mfa: number; zt: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Identity v8</h3>
    <div className="text-sm">{active}/{providers} active · {users.toLocaleString()} users · {auth.toLocaleString()} auth · MFA {mfa}% · {zt ? "✅ ZT" : "⚠️"}</div>
  </div>);
}
