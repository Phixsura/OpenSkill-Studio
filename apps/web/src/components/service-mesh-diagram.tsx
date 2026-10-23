"use client";

interface MeshNode { name: string; port: number; replicas: number; healthy: boolean; }
interface MeshConnection { from: string; to: string; protocol: string; timeoutMs: number; }
interface ServiceMeshDiagramProps { nodes: MeshNode[]; connections: MeshConnection[];
  healthy: number; unhealthy: number; }

export function ServiceMeshDiagram({ nodes, connections, healthy, unhealthy }: ServiceMeshDiagramProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Service Mesh</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">✓ {healthy} healthy</span>
          {unhealthy > 0 && <span className="text-red-500">✗ {unhealthy} unhealthy</span>}
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4">
        {nodes.map(n => (
          <div key={n.name} className={`rounded-lg border p-3 text-center ${n.healthy ? "border-green-300 dark:border-green-800" : "border-red-300 dark:border-red-800"}`}>
            <div className="text-sm font-mono font-medium">{n.name}</div>
            <div className="text-[10px] text-gray-400">:{n.port} · {n.replicas}x</div>
          </div>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {connections.map((c, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-1.5 text-xs">
            <span className="font-mono">{c.from}</span>
            <span className="text-gray-400">→</span>
            <span className="font-mono">{c.to}</span>
            <span className="text-gray-400 ml-auto">{c.protocol} · {c.timeoutMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
