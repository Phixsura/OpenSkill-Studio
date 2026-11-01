"use client";
export function FleetAiPinjectionPanel({ services, active, scanned, blocked, blockRate }: { services: number; active: number; scanned: number; blocked: number; blockRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Prompt Injection Defense</h3>
    <div className="text-sm">{active}/{services} active · {scanned.toLocaleString()} scanned · {blocked} blocked ({blockRate}%)</div>
  </div>);
}
