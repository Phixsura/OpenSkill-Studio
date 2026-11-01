"use client";
interface EpDep { endpoint: string; dependencies: string[]; depCount: number; }
interface EpDepMapPanelProps { endpoints: EpDep[]; mostComplex: string; maxDeps: number; }
export function EpDepMapPanel({ endpoints, mostComplex, maxDeps }: EpDepMapPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Endpoint Deps</h3>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints · most complex: {mostComplex} ({maxDeps} deps)</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="px-4 py-1.5 text-xs">
            <div className="font-mono font-semibold mb-0.5">{e.endpoint}</div>
            <div className="text-gray-400">{e.dependencies.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
