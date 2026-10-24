"use client";
export function FleetLaunchdarklyPanel({ total, active, stale, targeting }: { total: number; active: number; stale: number; targeting: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 LaunchDarkly</h3>
    <div className="text-sm">{active}/{total} active · {targeting} targeting · {stale} stale</div>
  </div>);
}
