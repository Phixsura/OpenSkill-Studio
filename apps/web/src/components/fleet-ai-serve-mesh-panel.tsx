"use client";
export function FleetAiServeMeshPanel({ nodes, healthy, rps, p99, gpuUtil }: { nodes: number; healthy: number; rps: number; p99: number; gpuUtil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Serving Mesh</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {rps.toLocaleString()} RPS · p99 {p99}ms · GPU {gpuUtil}%</div>
  </div>);
}
