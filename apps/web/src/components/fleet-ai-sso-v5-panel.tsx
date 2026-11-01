"use client";
export function FleetAiSsoV5Panel({ providers, active, logins, protocols, mfa }: { providers: number; active: number; logins: number; protocols: string[]; mfa: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI SSO v5</h3>
    <div className="text-sm">{active}/{providers} active · {logins.toLocaleString()} logins · {protocols.join(", ")} · {mfa ? "✅ MFA" : "⚠️"}</div>
  </div>);
}
