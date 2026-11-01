"use client";

interface TimelineEntry {
  status: string;
  message: string;
  timestamp: string;
}

interface IncidentInfo {
  incident_id: string;
  title: string;
  severity: "critical" | "major" | "minor";
  status: "investigating" | "identified" | "monitoring" | "resolved";
  affected_components: string[];
  timeline: TimelineEntry[];
  created_at: string;
  duration_minutes: number;
}

interface IncidentTrackerCardProps {
  incidents: IncidentInfo[];
  appName: string;
}

const SEVERITY_STYLES: Record<string, { bg: string; text: string }> = {
  critical: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
  major: {
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
  },
  minor: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
};

const STATUS_ICONS: Record<string, string> = {
  investigating: "🔍",
  identified: "🎯",
  monitoring: "👀",
  resolved: "✅",
};

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export default function IncidentTrackerCard({ incidents, appName }: IncidentTrackerCardProps) {
  const activeCount = incidents.filter((i) => i.status !== "resolved").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Incidents</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {activeCount} active
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All clear
          </span>
        )}
      </div>

      {incidents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No incidents</p>
      ) : (
        <div className="space-y-3">
          {incidents.map((inc) => {
            const sev = SEVERITY_STYLES[inc.severity] ?? SEVERITY_STYLES.minor;
            const icon = STATUS_ICONS[inc.status] ?? "❓";
            return (
              <div
                key={inc.incident_id}
                className={`rounded-lg border px-3 py-2.5 ${
                  inc.status !== "resolved"
                    ? "border-red-200 dark:border-red-900/50"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span>{icon}</span>
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {inc.title}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${sev.bg} ${sev.text}`}
                    >
                      {inc.severity}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {formatDuration(inc.duration_minutes)}
                  </span>
                </div>
                {inc.affected_components.length > 0 && (
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {inc.affected_components.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                )}
                {inc.timeline.length > 0 && (
                  <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
                    Latest: {inc.timeline[inc.timeline.length - 1].message}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
