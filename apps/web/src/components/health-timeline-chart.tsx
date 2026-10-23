"use client";

interface TimelinePoint { timestamp: string; status: string; response_ms: number; }
interface HealthTimelineChartProps { timeline: TimelinePoint[]; uptimePct: number; currentStatus: string; }

const STATUS_COLORS: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500", unknown: "bg-gray-300" };

export function HealthTimelineChart({ timeline, uptimePct, currentStatus }: HealthTimelineChartProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Uptime</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${STATUS_COLORS[currentStatus] || "bg-gray-300"}`} />
          <span className={`text-lg font-bold ${uptimePct >= 99.9 ? "text-green-600" : uptimePct >= 99 ? "text-yellow-600" : "text-red-600"}`}>
            {uptimePct}%
          </span>
        </div>
      </div>
      <div className="mt-3 flex gap-px">
        {timeline.slice(-90).map((t, i) => (
          <div key={i} className={`h-8 flex-1 rounded-sm ${STATUS_COLORS[t.status] || "bg-gray-200"}`}
            title={`${t.timestamp.slice(0, 10)}: ${t.status}`} />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>90 days ago</span><span>Today</span>
      </div>
    </div>
  );
}
