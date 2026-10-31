"use client";
export function FleetRenovatePanel({ total, enabled, openPrs, merged }: { total: number; enabled: number; openPrs: number; merged: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Renovate</h3>
    <div className="text-sm">{enabled}/{total} enabled · {openPrs} open PRs · {merged} merged/30d</div>
  </div>);
}
