"use client";

interface TimelineEvent { time: string; type: string; message: string; author?: string; severity?: string; }
interface IncidentTimelineViewProps { incidentId: string; events: TimelineEvent[]; durationMinutes: number | null; }

const EVENT_ICONS: Record<string, string> = { opened: "🔴", update: "🔵", resolved: "✅", escalated: "🟠" };

export function IncidentTimelineView({ incidentId, events, durationMinutes }: IncidentTimelineViewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Incident Timeline</h3>
        <span className="text-xs text-gray-400">
          {durationMinutes != null ? `${durationMinutes} min` : "Ongoing"}
        </span>
      </div>
      <div className="mt-3 space-y-0">
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 pb-3">
            <div className="flex flex-col items-center">
              <span className="text-sm">{EVENT_ICONS[e.type] || "📌"}</span>
              {i < events.length - 1 && <div className="mt-1 w-px flex-1 bg-gray-200 dark:bg-gray-700" />}
            </div>
            <div>
              <p className="text-sm">{e.message}</p>
              <p className="text-xs text-gray-400">{e.time?.slice(11, 16)} {e.author ? `· ${e.author}` : ""}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
