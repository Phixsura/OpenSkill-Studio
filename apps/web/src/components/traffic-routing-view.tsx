"use client";

interface Target { backend: string; weight: number; }
interface Route { path: string; targets: Target[]; }
interface TrafficRoutingViewProps { routes: Route[]; routeCount: number; }

export function TrafficRoutingView({ routes, routeCount }: TrafficRoutingViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Traffic Routing</h3>
        <span className="text-xs text-gray-400">{routeCount} routes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map(r => (
          <div key={r.path} className="px-4 py-3">
            <div className="text-sm font-mono font-medium mb-1.5">{r.path}</div>
            <div className="flex gap-2">
              {r.targets.map(t => (
                <div key={t.backend} className="flex-1">
                  <div className="flex justify-between text-[10px] mb-0.5">
                    <span className="font-mono">{t.backend}</span>
                    <span className="text-gray-400">{t.weight}%</span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${t.weight}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
