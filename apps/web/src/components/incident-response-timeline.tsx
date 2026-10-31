"use client";

interface TimelineEntry { action: string; message?: string; by: string; at: string; }
interface IncidentResponseTimelineProps { incidentId: string; title: string; severity: string;
  severityLabel: string; status: string; affectedServices: string[];
  timeline: TimelineEntry[]; onUpdate: () => void; }

const sevColor: Record<string, string> = {
  sev1: "bg-red-100 text-red-700 dark:bg-red-900/30", sev2: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  sev3: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", sev4: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
};
const statusIcon: Record<string, string> = {
  investigating: "🔍", identified: "🎯", monitoring: "👁️", resolved: "✅",
};

export function IncidentResponseTimeline({ incidentId, title, severity, severityLabel,
  status, affectedServices, timeline, onUpdate }: IncidentResponseTimelineProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-gray-400">{incidentId}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs ${sevColor[severity] ?? ""}`}>{severityLabel}</span>
          </div>
          <h2 className="mt-1 text-lg font-semibold">{title}</h2>
          <div className="mt-1 flex gap-1">
            {affectedServices.map(s => (
              <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{s}</span>
            ))}
          </div>
        </div>
        <span className="text-lg">{statusIcon[status] ?? "❓"}</span>
      </div>
      <div className="border-l-2 border-gray-200 pl-4 dark:border-gray-700">
        {timeline.map((t, i) => (
          <div key={i} className="relative mb-3">
            <div className="absolute -left-[1.35rem] h-2.5 w-2.5 rounded-full bg-blue-500" />
            <p className="text-sm font-medium capitalize">{t.action}</p>
            {t.message && <p className="text-xs text-gray-500">{t.message}</p>}
            <p className="text-xs text-gray-400">{t.by} · {new Date(t.at).toLocaleTimeString()}</p>
          </div>
        ))}
      </div>
      {status !== "resolved" && (
        <button onClick={onUpdate} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Post Update</button>
      )}
    </div>
  );
}
