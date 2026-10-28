"use client";

interface AuditEventInfo {
  event_id: string;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  severity: "info" | "warning" | "critical";
  details: string;
  ip_address: string;
  timestamp: string;
}

interface AuditLogCardProps {
  events: AuditEventInfo[];
  appName: string;
  totalCount: number;
}

const SEVERITY_STYLES: Record<string, { dot: string; text: string }> = {
  info: { dot: "bg-blue-400", text: "text-blue-600 dark:text-blue-400" },
  warning: { dot: "bg-yellow-500", text: "text-yellow-600 dark:text-yellow-400" },
  critical: { dot: "bg-red-500", text: "text-red-600 dark:text-red-400" },
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function AuditLogCard({ events, appName, totalCount }: AuditLogCardProps) {
  const criticalCount = events.filter((e) => e.severity === "critical").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Audit Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          {criticalCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {criticalCount} critical
            </span>
          )}
          <span className="text-xs text-gray-400">{totalCount.toLocaleString()} total</span>
        </div>
      </div>

      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit events</p>
      ) : (
        <div className="space-y-1">
          {events.map((evt) => {
            const sev = SEVERITY_STYLES[evt.severity] ?? SEVERITY_STYLES.info;
            return (
              <div
                key={evt.event_id}
                className="flex items-start gap-2.5 rounded px-2 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${sev.dot}`} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-medium ${sev.text}`}>{evt.action}</span>
                    <span className="text-[11px] text-gray-400">
                      {evt.resource_type}/{evt.resource_id}
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-2 text-[11px] text-gray-400">
                    <span>{evt.actor}</span>
                    {evt.ip_address && (
                      <>
                        <span>·</span>
                        <span>{evt.ip_address}</span>
                      </>
                    )}
                    <span>·</span>
                    <span>{timeAgo(evt.timestamp)}</span>
                  </div>
                  {evt.details && (
                    <p className="mt-0.5 truncate text-[11px] text-gray-500 dark:text-gray-400">
                      {evt.details}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
