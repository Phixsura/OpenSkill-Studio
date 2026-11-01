"use client";
export function FleetServiceMeshSecurityV9Panel({ policies, mtls }: { policies: number; mtls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Mesh Security v9</h3>
    <div className="text-sm">{policies} policies · {mtls} mTLS</div>
  </div>);
}
