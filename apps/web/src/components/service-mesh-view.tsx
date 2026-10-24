"use client";

interface MeshNode { id: string; name: string; status: string; rps: number;
  upstream: string[]; downstream: string[]; }
interface ServiceMeshViewProps { nodes: MeshNode[]; totalConnections: number;
  meshHealth: string; criticalPath: string[]; }

const STATUS_DOT: Record<string, string> = {
  healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500",
};

export function ServiceMeshView({ nodes, totalConnections, meshHealth, criticalPath }: ServiceMeshViewProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🕸️ Service Mesh</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{nodes.length} services · {totalConnections} connections</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            meshHealth === "healthy" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
          }`}>{meshHealth}</span>
        </div>
      </div>
      {criticalPath.length > 0 && (
        <div className="mb-3 p-2 bg-orange-50 dark:bg-orange-900/20 rounded text-xs text-orange-700 dark:text-orange-400">
          ⚡ Critical path: {criticalPath.join(" → ")}
        </div>
      )}
      <div className="grid grid-cols-2 gap-3">
        {nodes.map(n => (
          <div key={n.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-2.5 h-2.5 rounded-full ${STATUS_DOT[n.status] || "bg-gray-400"}`} />
              <span className="text-sm font-medium">{n.name}</span>
            </div>
            <div className="text-xs text-gray-400">
              <span>{n.rps.toLocaleString()} rps</span>
              <span className="mx-1">·</span>
              <span>{n.downstream.length} downstream</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
