"use client";

interface TimelineEvent {
  message: string;
  author: string;
  status: string;
  timestamp: string;
}

interface Incident {
  id: string;
  title: string;
  severity: "sev1" | "sev2" | "sev3" | "sev4";
  status: string;
  assignee?: string;
  affectedUsers: number;
  rootCause?: string;
  mttrMinutes: number;
  timeline: TimelineEvent[];
}

const sevConfig: Record<string, { color: string; label: string }> = {
  sev1: { color: "bg-red-600 text-white", label: "SEV1" },
  sev2: { color: "bg-orange-500 text-white", label: "SEV2" },
  sev3: { color: "bg-yellow-500 text-white", label: "SEV3" },
  sev4: { color: "bg-gray-400 text-white", label: "SEV4" },
};

const statusColors: Record<string, string> = {
  open: "text-red-600", investigating: "text-blue-600", identified: "text-purple-600",
  mitigating: "text-yellow-600", resolved: "text-green-600", postmortem: "text-gray-600",
};

export function IncidentTimelinePanel({
  incident,
  onUpdateStatus,
  onAssign,
}: {
  incident: Incident;
  onUpdateStatus?: (status: string) => void;
  onAssign?: (assignee: string) => void;
}) {
  const sev = sevConfig[incident.severity];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded font-bold ${sev.color}`}>{sev.label}</span>
          <h2 className="text-lg font-bold">{incident.title}</h2>
        </div>
        <span className={`text-sm font-bold capitalize ${statusColors[incident.status] || ""}`}>{incident.status}</span>
      </div>

      <div className="flex gap-4 text-xs text-gray-500">
        {incident.assignee && <span>👤 {incident.assignee}</span>}
        <span>👥 {incident.affectedUsers.toLocaleString()} affected</span>
        {incident.mttrMinutes > 0 && <span>⏱ {incident.mttrMinutes}min MTTR</span>}
      </div>

      {incident.rootCause && (
        <div className="text-sm bg-yellow-50 dark:bg-yellow-900/10 rounded-lg p-3">
          <span className="font-medium">Root Cause:</span> {incident.rootCause}
        </div>
      )}

      <div className="relative">
        <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />
        {incident.timeline.map((evt, i) => (
          <div key={i} className="relative pl-8 pb-3">
            <div className={`absolute left-1.5 w-3 h-3 rounded-full mt-1 ${statusColors[evt.status] ? "bg-blue-500" : "bg-gray-400"}`} />
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold capitalize ${statusColors[evt.status] || ""}`}>{evt.status}</span>
                <span className="text-xs text-gray-400">{evt.author} · {evt.timestamp}</span>
              </div>
              <p className="text-sm">{evt.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
