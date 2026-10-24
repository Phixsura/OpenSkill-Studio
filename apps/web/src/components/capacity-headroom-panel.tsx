"use client";
interface Headroom { service: string; currentRps: number; maxRps: number; headroomPct: number; status: string; }
interface CapacityHeadroomPanelProps { services: Headroom[]; bottleneck: string; minHeadroomPct: number; }
const STATUS_COLOR: Record<string, string> = { ok: "text-green-600", warning: "text-yellow-600", critical: "text-red-500" };
export function CapacityHeadroomPanel({ services, bottleneck, minHeadroomPct }: CapacityHeadroomPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Capacity Headroom</h3>
        <span className={`text-xs font-bold ${minHeadroomPct < 20 ? "text-yellow-600" : "text-green-600"}`}>
          min: {minHeadroomPct}% · bottleneck: {bottleneck}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{s.service}</span>
              <span className={STATUS_COLOR[s.status] ?? ""}>{s.currentRps}/{s.maxRps} rps ({s.headroomPct}% free)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${s.status === "critical" ? "bg-red-500" : s.status === "warning" ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${100 - s.headroomPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
