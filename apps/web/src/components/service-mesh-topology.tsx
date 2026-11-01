"use client";

interface Node { id: string; name: string; type: string; healthy: boolean; }
interface Edge { from: string; to: string; protocol: string; }
interface ServiceMeshTopologyProps { nodes: Node[]; edges: Edge[]; meshHealth: string; }

export function ServiceMeshTopology({ nodes, edges, meshHealth }: ServiceMeshTopologyProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Service Mesh</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${meshHealth === "healthy" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {meshHealth}
        </span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {nodes.map(n => {
          const outgoing = edges.filter(e => e.from === n.id);
          return (
            <div key={n.id} className={`rounded-lg border p-3 ${n.healthy ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${n.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="font-medium">{n.name}</span>
              </div>
              <p className="mt-0.5 text-xs text-gray-400">{n.type}</p>
              {outgoing.length > 0 && (
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {outgoing.map(e => (
                    <span key={e.to} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">
                      → {nodes.find(nd => nd.id === e.to)?.name ?? e.to}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
