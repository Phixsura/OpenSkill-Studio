"use client";
export function FleetAiSvcMeshPanel({ meshes, active, services, requests, p99 }: { meshes: number; active: number; services: number; requests: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Service Mesh</h3>
    <div className="text-sm">{active}/{meshes} active · {services} services · {requests.toLocaleString()} req · p99 {p99}ms</div>
  </div>);
}
