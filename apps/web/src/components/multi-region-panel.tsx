"use client";

interface RegionInfo { id: string; label: string; healthy: boolean; trafficPct: number; }
interface MultiRegionPanelProps { primary: string; status: string;
  regions: RegionInfo[]; onFailover: (regionId: string) => void; }

export function MultiRegionPanel({ primary, status, regions, onFailover }: MultiRegionPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🌍 Multi-Region</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          status === "healthy" ? "bg-green-100 text-green-700" :
          status === "degraded" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{status}</span>
      </div>
      <div className="space-y-2">
        {regions.map(r => (
          <div key={r.id} className={`flex items-center justify-between rounded-lg px-4 py-3 ${
            r.id === primary ? "bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800" : "bg-gray-50 dark:bg-gray-800"
          }`}>
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${r.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{r.label}</span>
              {r.id === primary && <span className="text-xs text-blue-600">Primary</span>}
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400">{r.trafficPct}% traffic</span>
              {r.id !== primary && r.healthy && (
                <button onClick={() => onFailover(r.id)}
                  className="text-xs px-2 py-1 border border-blue-200 text-blue-600 rounded hover:bg-blue-50">Promote</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
