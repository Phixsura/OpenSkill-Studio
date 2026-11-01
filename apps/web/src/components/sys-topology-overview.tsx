"use client";

interface LayerStats { services: number; healthy: number; connections: number; }
interface SysTopologyOverviewProps { layers: Record<string, LayerStats>;
  totalServices: number; totalConnections: number; }

const LAYER_ICONS: Record<string, string> = {
  frontend: "🖥️", backend: "⚙️", data: "💾", infrastructure: "🏗️",
};

export function SysTopologyOverview({ layers, totalServices, totalConnections }: SysTopologyOverviewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ System Topology</h3>
        <span className="text-xs text-gray-400">{totalServices} services · {totalConnections} connections</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(layers).map(([name, stats]) => (
          <div key={name} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
              <span>{LAYER_ICONS[name] ?? "📦"}</span>
              <span className="text-sm font-medium capitalize">{name}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{stats.services} services</span>
              <span className="text-green-600">{stats.healthy} healthy</span>
              <span>{stats.connections} connections</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
