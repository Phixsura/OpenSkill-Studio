"use client";
interface Route { pathPrefix: string; backend: string; weight: number; }
interface GwRouterPanelProps { routes: Route[]; }
export function GwRouterPanel({ routes }: GwRouterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Gateway Router</h3>
        <span className="text-xs text-gray-400">{routes.length} routes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map((r, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.pathPrefix}</span>
            <span className="text-gray-400">{r.backend} · w:{r.weight}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
