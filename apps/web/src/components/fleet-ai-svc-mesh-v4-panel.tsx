"use client";
export function FleetAiSvcMeshV4Panel({ meshes, active, services, requests, mtls }: { meshes: number; active: number; services: number; requests: number; mtls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Service Mesh v4</h3>
    <div className="text-sm">{active}/{meshes} active · {services} services · {requests.toLocaleString()} req · mTLS {mtls}%</div>
  </div>);
}
