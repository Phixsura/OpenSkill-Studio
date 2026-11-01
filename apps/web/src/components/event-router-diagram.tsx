"use client";

interface Route { pattern: string; handler: string; hits: number; }
interface EventRouterDiagramProps { routes: Route[]; totalRoutes: number; }

export function EventRouterDiagram({ routes, totalRoutes }: EventRouterDiagramProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Event Router</h3>
        <span className="text-xs text-gray-400">{totalRoutes} routes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono text-blue-500">{r.pattern}</span>
              <span className="text-gray-400">→</span>
              <span className="font-mono text-green-600">{r.handler}</span>
            </div>
            <span className="text-gray-400">{r.hits} hits</span>
          </div>
        ))}
      </div>
    </div>
  );
}
