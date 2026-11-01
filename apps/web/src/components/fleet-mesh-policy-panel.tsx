"use client";
export function FleetMeshPolicyPanel({ total, withPolicy, defaultDeny, zeroTrust }: { total: number; withPolicy: number; defaultDeny: number; zeroTrust: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Mesh Policies</h3>
    <div className="text-sm">{withPolicy}/{total} with policy · {defaultDeny} default-deny</div>
    <span className={`text-xs ${zeroTrust ? "text-green-600" : "text-yellow-600"}`}>{zeroTrust ? "✅ Zero Trust" : "⚠️ Not zero trust"}</span>
  </div>);
}
