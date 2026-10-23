"use client";

interface MeshService { name: string; port: number; protocol: string; health: string; depCount: number; hasSidecar: boolean; }
interface MeshPolicy { source: string; destination: string; allowed: boolean; mtls: boolean; }
interface ServiceMeshDiagramProps { services: MeshService[]; policies: MeshPolicy[];
  totalConnections: number; mtlsEnabled: boolean; }

const healthDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-red-500" };

export function ServiceMeshDiagram({ services, policies, totalConnections, mtlsEnabled }: ServiceMeshDiagramProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Service Mesh</h3>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>{services.length} services</span>
          <span>{totalConnections} connections</span>
          <span className={mtlsEnabled ? "text-green-600" : "text-yellow-600"}>
            {mtlsEnabled ? "🔒 mTLS" : "⚠ No mTLS"}
          </span>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {services.map(s => (
          <div key={s.name} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${healthDot[s.health] ?? "bg-gray-400"}`} />
              <span className="text-sm font-semibold">{s.name}</span>
              {s.hasSidecar && <span className="text-xs text-blue-500">🛡️</span>}
            </div>
            <p className="mt-1 text-xs text-gray-400">{s.protocol}://:{s.port} · {s.depCount} deps</p>
          </div>
        ))}
      </div>
    </div>
  );
}
