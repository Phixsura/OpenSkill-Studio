"use client";
export function FleetAiContentFltPanel({ filters, active, scanned, blocked, blockRate }: { filters: number; active: number; scanned: number; blocked: number; blockRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Content Filter</h3>
    <div className="text-sm">{active}/{filters} active · {scanned.toLocaleString()} scanned · {blocked.toLocaleString()} blocked ({blockRate}%)</div>
  </div>);
}
