"use client";

interface Region { name: string; role: string; healthy: boolean; }
interface RegionFailoverPanelProps { regions: Region[]; primary: string | null;
  failoverNeeded: boolean; onFailover: (region: string) => void; }

export function RegionFailoverPanel({ regions, primary, failoverNeeded, onFailover }: RegionFailoverPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Multi-Region</h3>
        {failoverNeeded && <span className="text-xs text-red-500 font-medium">⚠ Failover Needed</span>}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {regions.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${r.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{r.name}</span>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${r.role === "primary" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"}`}>{r.role}</span>
            </div>
            {r.role === "standby" && r.healthy && failoverNeeded && (
              <button onClick={() => onFailover(r.name)}
                className="px-2 py-1 text-xs bg-red-500 text-white rounded">Promote</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
