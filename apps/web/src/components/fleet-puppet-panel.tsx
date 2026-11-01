"use client";
export function FleetPuppetPanel({ total, inSync, changed, failed }: { total: number; inSync: number; changed: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 Puppet</h3>
    <div className="text-sm">{inSync} sync · {changed} changed · {failed} failed of {total}</div>
  </div>);
}
