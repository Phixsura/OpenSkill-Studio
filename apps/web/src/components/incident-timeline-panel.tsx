"use client";

interface IncidentEvent { eventId: string; status: string; message: string; timestamp: number; }
interface Incident { incidentId: string; title: string; severity: string; resolved: boolean; events: IncidentEvent[]; }

const sevColors: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  major: "bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400",
  minor: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400",
};

const statusIcons: Record<string, string> = {
  investigating: "🔍", identified: "🎯", monitoring: "👁️", resolved: "✅",
};

export function IncidentTimelinePanel({ incidents }: { incidents: Incident[] }) {
  if (!incidents.length) {
    return <div className="text-center text-green-600 py-8"><span className="text-3xl block">✅</span><span className="font-semibold mt-2 block">All Systems Operational</span><span className="text-xs text-gray-500">No active incidents</span></div>;
  }
  return (
    <div className="space-y-4">
      {incidents.map((inc) => (
        <div key={inc.incidentId} className="border dark:border-gray-700 rounded-xl overflow-hidden">
          <div className="p-3 flex items-center justify-between bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sevColors[inc.severity] || ""}`}>{inc.severity}</span>
              <span className="font-semibold text-sm">{inc.title}</span>
            </div>
            {inc.resolved && <span className="text-xs text-green-600 font-medium">Resolved</span>}
          </div>
          <div className="p-3 space-y-2">
            {inc.events.map((evt) => (
              <div key={evt.eventId} className="flex gap-2 text-xs">
                <span>{statusIcons[evt.status] || "📌"}</span>
                <div>
                  <span className="font-medium capitalize">{evt.status}</span>
                  <span className="text-gray-500 ml-1">— {evt.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
