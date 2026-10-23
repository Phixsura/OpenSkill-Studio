"use client";

interface Incident { id: string; title: string; severity: string; started: string; resolved: string; duration_min: number; affected: string[]; }
interface IncidentTimelineDisplayProps { incidents: Incident[]; uptimePct: number; mttrMin: number; }

const severityColors: Record<string, string> = {
  minor: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  major: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export function IncidentTimelineDisplay({ incidents, uptimePct, mttrMin }: IncidentTimelineDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Incident History</h2>
        <div className="flex gap-3 text-sm">
          <span>Uptime: <strong className="text-green-600">{uptimePct}%</strong></span>
          <span>MTTR: <strong>{mttrMin}m</strong></span>
        </div>
      </div>
      <div className="space-y-3">
        {incidents.map(inc => (
          <div key={inc.id} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium">{inc.title}</p>
                <p className="mt-0.5 text-xs text-gray-400">{new Date(inc.started).toLocaleDateString()} · {inc.duration_min}m</p>
              </div>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityColors[inc.severity] ?? ""}`}>
                {inc.severity}
              </span>
            </div>
            <div className="mt-1.5 flex gap-1">
              {inc.affected.map(a => (
                <span key={a} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{a}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
