"use client";

interface AvailZonesPanelProps { totalZones: number; healthy: number;
  unhealthy: number; regions: number; byRegion: Record<string, number>;
  multiAz: boolean; allHealthy: boolean; }

export function AvailZonesPanel({ totalZones, healthy, unhealthy, regions, byRegion, multiAz, allHealthy }: AvailZonesPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Availability Zones</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalZones} zones · {regions} regions</span>
          <span className={allHealthy ? "text-green-600" : "text-yellow-600"}>
            {allHealthy ? "✅ All Healthy" : `⚠ ${unhealthy} unhealthy`}
          </span>
        </div>
      </div>
      <div className="p-3 flex flex-wrap gap-2">
        {Object.entries(byRegion).map(([region, count]) => (
          <span key={region} className="px-2 py-1 text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded">
            {region}: {count} AZs
          </span>
        ))}
      </div>
      {multiAz && <div className="px-4 py-2 border-t dark:border-gray-700 text-[10px] text-green-600">✅ Multi-AZ deployment active</div>}
    </div>
  );
}
