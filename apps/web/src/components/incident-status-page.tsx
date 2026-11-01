"use client";

interface TimelineEvent {
  status: string;
  message: string;
  timestamp: string;
  author: string;
}

interface Incident {
  incident_id: string;
  title: string;
  severity: "critical" | "major" | "minor" | "info";
  status: "investigating" | "identified" | "monitoring" | "resolved";
  affected_components: string[];
  timeline: TimelineEvent[];
  created_at: string;
  duration_minutes: number | null;
}

interface IncidentSummary {
  total: number;
  open: number;
  resolved: number;
  mttr_minutes: number | null;
}

interface IncidentStatusPageProps {
  appName: string;
  incidents: Incident[];
  summary: IncidentSummary;
}

const SEV_STYLES: Record<string, { label: string; dot: string }> = {
  critical: { label: "Critical", dot: "bg-red-500" },
  major: { label: "Major", dot: "bg-orange-500" },
  minor: { label: "Minor", dot: "bg-yellow-500" },
  info: { label: "Info", dot: "bg-blue-500" },
};

const STATUS_STYLES: Record<string, { label: string; color: string }> = {
  investigating: {
    label: "Investigating",
    color: "text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-300",
  },
  identified: {
    label: "Identified",
    color: "text-orange-600 bg-orange-100 dark:bg-orange-900/20 dark:text-orange-300",
  },
  monitoring: {
    label: "Monitoring",
    color: "text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300",
  },
  resolved: {
    label: "Resolved",
    color: "text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-300",
  },
};

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function IncidentCard({ incident }: { incident: Incident }) {
  const sev = SEV_STYLES[incident.severity] ?? SEV_STYLES.info;
  const st = STATUS_STYLES[incident.status] ?? STATUS_STYLES.investigating;

  return (
    <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${sev.dot}`} />
          <h4 className="text-sm font-semibold">{incident.title}</h4>
        </div>
        <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${st.color}`}>
          {st.label}
        </span>
      </div>

      {incident.affected_components.length > 0 && (
        <div className="mt-1 flex gap-1">
          {incident.affected_components.map((c) => (
            <span
              key={c}
              className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800"
            >
              {c}
            </span>
          ))}
        </div>
      )}

      {incident.duration_minutes !== null && (
        <p className="mt-1 text-[10px] text-gray-400">
          Duration:{" "}
          {incident.duration_minutes < 60
            ? `${Math.round(incident.duration_minutes)}m`
            : `${(incident.duration_minutes / 60).toFixed(1)}h`}
        </p>
      )}

      <div className="mt-2 space-y-1 border-t border-gray-100 pt-2 dark:border-gray-800">
        {incident.timeline.slice(0, 3).map((e, i) => (
          <div key={i} className="flex items-start gap-2 text-[10px]">
            <span className="shrink-0 text-gray-400">{formatTime(e.timestamp)}</span>
            <span className="text-gray-600 dark:text-gray-400">{e.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function IncidentStatusPage({ appName, incidents, summary }: IncidentStatusPageProps) {
  const allClear = summary.open === 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Incident Status</h2>
          <p className="text-xs text-gray-500">{appName}</p>
        </div>
        <div
          className={`rounded-full px-3 py-1 text-xs font-semibold ${allClear ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"}`}
        >
          {allClear
            ? "✓ All Systems Operational"
            : `${summary.open} Active Incident${summary.open !== 1 ? "s" : ""}`}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border border-gray-200 p-2.5 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{summary.total}</p>
          <p className="text-[10px] text-gray-500">Total</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-2.5 text-center dark:border-gray-700">
          <p className={`text-lg font-bold ${summary.open > 0 ? "text-red-600" : ""}`}>
            {summary.open}
          </p>
          <p className="text-[10px] text-gray-500">Open</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-2.5 text-center dark:border-gray-700">
          <p className="text-lg font-bold text-green-600">{summary.resolved}</p>
          <p className="text-[10px] text-gray-500">Resolved</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-2.5 text-center dark:border-gray-700">
          <p className="text-lg font-bold">
            {summary.mttr_minutes !== null ? `${summary.mttr_minutes}m` : "—"}
          </p>
          <p className="text-[10px] text-gray-500">MTTR</p>
        </div>
      </div>

      {/* Incidents */}
      {incidents.length === 0 ? (
        <div className="rounded-lg border border-gray-200 py-8 text-center dark:border-gray-700">
          <span className="text-3xl">🎉</span>
          <p className="mt-2 text-sm text-gray-500">No incidents recorded</p>
        </div>
      ) : (
        <div className="space-y-2">
          {incidents.map((inc) => (
            <IncidentCard key={inc.incident_id} incident={inc} />
          ))}
        </div>
      )}
    </div>
  );
}
