"use client";
export function FleetSnykPanel({ total, clean, totalIssues, critical }: { total: number; clean: number; totalIssues: number; critical: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Snyk</h3>
    <div className="text-sm">{clean}/{total} clean · {totalIssues} issues</div>
    {critical > 0 && <span className="text-xs text-red-500">🚨 {critical} critical</span>}
  </div>);
}
