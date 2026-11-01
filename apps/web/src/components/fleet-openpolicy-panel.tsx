"use client";
export function FleetOpenpolicyPanel({ total, withPolicy, ciEnforced, coveragePct }: { total: number; withPolicy: number; ciEnforced: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Policy-as-Code</h3>
    <div className="text-sm">{withPolicy}/{total} with policy ({coveragePct}%) · {ciEnforced} CI enforced</div>
  </div>);
}
