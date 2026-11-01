"use client";

interface TimelineEvent { action: string; note?: string; by?: string; }
interface IncidentTimelineViewProps { incidentId: string; title: string;
  severity: string; status: string; events: TimelineEvent[];
  commander: string; affected: string[]; }

const SEV_STYLE: Record<string, string> = {
  sev1: "bg-red-100 text-red-700", sev2: "bg-orange-100 text-orange-700",
  sev3: "bg-yellow-100 text-yellow-700", sev4: "bg-blue-100 text-blue-700",
};

export function IncidentTimelineView({ incidentId, title, severity, status, events, commander, affected }: IncidentTimelineViewProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <div>
          <span className="text-xs font-mono text-gray-400">{incidentId}</span>
          <h3 className="font-semibold">{title}</h3>
        </div>
        <div className="flex gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ${SEV_STYLE[severity] || ""}`}>{severity}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${status === "resolved" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{status}</span>
        </div>
      </div>
      <div className="flex gap-3 text-xs text-gray-400 mb-4">
        <span>Commander: {commander}</span>
        <span>Affected: {affected.join(", ")}</span>
      </div>
      <div className="border-l-2 border-gray-200 dark:border-gray-700 space-y-3 pl-4">
        {events.map((e, i) => (
          <div key={i}>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 -ml-5" />
              <span className="text-sm font-medium capitalize">{e.action}</span>
              {e.by && <span className="text-xs text-gray-400">by {e.by}</span>}
            </div>
            {e.note && <p className="text-xs text-gray-500 mt-0.5">{e.note}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
