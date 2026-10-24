"use client";
interface Region { name: string; status: string; isPrimary: boolean; }
interface RegionFailoverPanelProps { regions: Region[]; primary: string; failed: string[]; }
export function RegionFailoverPanel({ regions, primary, failed }: RegionFailoverPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌎 Region Failover</h3>
        <span className={`text-xs font-bold ${failed.length > 0 ? "text-red-500" : "text-green-600"}`}>
          primary: {primary}{failed.length > 0 ? ` · ${failed.length} failed` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {regions.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${r.status === "active" ? "bg-green-500" : "bg-red-500"}`} />
              <span className={`font-mono ${r.isPrimary ? "font-bold" : ""}`}>{r.name}</span>
            </div>
            <div className="flex gap-1">
              {r.isPrimary && <span className="text-[10px] bg-blue-100 text-blue-700 px-1 rounded">PRIMARY</span>}
              <span className={r.status === "active" ? "text-green-600" : "text-red-500"}>{r.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
