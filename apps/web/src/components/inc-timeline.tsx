"use client";

interface TimelineEvent { type: string; message?: string; }
interface IncTimelineProps { events: TimelineEvent[]; durationMin: number; eventCount: number; }

const TYPE_ICONS: Record<string, string> = {
  alert: "🔴", ack: "👁️", investigating: "🔍", identified: "🎯",
  mitigating: "🔧", resolved: "✅", update: "📝",
};

export function IncTimeline({ events, durationMin, eventCount }: IncTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Incident Timeline</h3>
        <span className="text-xs text-gray-400">{eventCount} events · {durationMin}min</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
            <span>{TYPE_ICONS[e.type] ?? "⚪"}</span>
            <span className="capitalize font-medium">{e.type}</span>
            {e.message && <span className="text-gray-400">{e.message}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
