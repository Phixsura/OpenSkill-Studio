"use client";

interface TimelineEvent { timestamp: number; phase: string; msg: string; }
interface IncidentTimelineProps { events: TimelineEvent[]; mttrMinutes: number; }

const PHASE_COLOR: Record<string, string> = {
  detect: "bg-red-500", triage: "bg-yellow-500", resolve: "bg-green-500",
};

export function IncidentTimeline({ events, mttrMinutes }: IncidentTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Incident Timeline</h3>
        <span className="text-xs text-gray-400">MTTR: {mttrMinutes}min · {events.length} events</span>
      </div>
      <div className="p-4 space-y-3">
        {events.map((e, i) => (
          <div key={i} className="flex items-start gap-3 text-xs">
            <div className={`w-2 h-2 mt-1 rounded-full ${PHASE_COLOR[e.phase] ?? "bg-gray-400"}`} />
            <div>
              <span className="font-semibold uppercase text-gray-500">{e.phase}</span>
              <div>{e.msg}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
