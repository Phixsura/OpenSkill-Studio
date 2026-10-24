"use client";

interface TimelineEntry { healthy: boolean; }
interface HealthTimelineChartProps { timeline: TimelineEntry[]; uptimePct: number;
  incidents: number; windowHours: number; improving: boolean | null; }

export function HealthTimelineChart({ timeline, uptimePct, incidents, windowHours, improving }: HealthTimelineChartProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Health Timeline ({windowHours}h)</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{uptimePct}% uptime</span>
          <span className="text-gray-400">{incidents} incidents</span>
          {improving !== null && (
            <span className={improving ? "text-green-600" : "text-red-500"}>{improving ? "↑" : "↓"}</span>
          )}
        </div>
      </div>
      <div className="p-3 flex gap-0.5">
        {timeline.map((e, i) => (
          <div key={i} className={`flex-1 h-6 rounded-sm ${e.healthy ? "bg-green-400" : "bg-red-400"}`}
            title={e.healthy ? "Healthy" : "Unhealthy"} />
        ))}
      </div>
    </div>
  );
}
