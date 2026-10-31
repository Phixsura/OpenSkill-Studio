"use client";
export function FleetPodSecPanel({ total, privileged, runAsRoot, compliant }: { total: number; privileged: number; runAsRoot: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Pod Security</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} pods compliant</span>
     : <span className="text-xs text-red-500">⚠️ {privileged} privileged · {runAsRoot} root</span>}
  </div>);
}
