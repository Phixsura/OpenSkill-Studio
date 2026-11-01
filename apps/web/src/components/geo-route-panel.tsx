"use client";

interface Region { name: string; endpoint: string; status: string; distanceKm: number; }
interface GeoRoutePanelProps { regions: Region[]; selectedRegion: string; healthy: number; total: number; }

export function GeoRoutePanel({ regions, selectedRegion, healthy, total }: GeoRoutePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Geo Routing</h3>
        <span className="text-xs text-gray-400">→ {selectedRegion} · {healthy}/{total} healthy</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {regions.map(r => (
          <div key={r.name} className={`flex items-center justify-between px-4 py-2 text-xs ${r.name === selectedRegion ? "bg-blue-50 dark:bg-blue-950" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${r.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-semibold">{r.name}</span>
            </div>
            <span className="text-gray-400">{r.distanceKm.toLocaleString()}km · {r.endpoint}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
