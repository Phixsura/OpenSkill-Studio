"use client";

interface NodeInfo { service_id: string; name: string; dependencies: string[]; dependents: string[]; health: string; }
interface Props { services: NodeInfo[]; appName: string; }

const hDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500" };

export default function APIDeveloperAPIApiDependencyGraphCard({ services, appName }: Props) {
  const downCount = services.filter(s => s.health === "down").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Dependency Graph</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {services.length} services</p>
        </div>
        {downCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{downCount} down</span>}
      </div>
      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services</p>
      ) : (
        <div className="space-y-1.5">
          {services.map((s) => (
            <div key={s.service_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${hDot[s.health] ?? "bg-gray-400"}`} />
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.name}</span>
              </div>
              <span className="text-gray-400">{s.dependencies.length} deps · {s.dependents.length} dependents</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
