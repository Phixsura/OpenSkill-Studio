"use client";
interface TimelineEntry { healthPct: number; status: string; }
interface MeshTimelinePanelProps { entries: TimelineEntry[]; trend: string; currentPct: number; dataPoints: number; }
const TREND_COLOR: Record<string, string> = { improving: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function MeshTimelinePanel({ entries, trend, currentPct, dataPoints }: MeshTimelinePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Mesh Health Timeline</h3>
        <span className={`text-xs font-bold ${TREND_COLOR[trend] ?? ""}`}>
          {trend} · {currentPct}% healthy · {dataPoints} points
        </span>
      </div>
      <div className="p-4 flex items-end gap-0.5 h-12">
        {entries.map((e, i) => (
          <div key={i} className={`flex-1 rounded-t ${e.status === "healthy" ? "bg-green-500" : e.status === "degraded" ? "bg-yellow-500" : "bg-red-500"}`}
            style={{ height: `${e.healthPct}%` }} title={`${e.healthPct}%`} />
        ))}
      </div>
    </div>
  );
}
