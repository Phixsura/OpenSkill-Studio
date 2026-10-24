"use client";

interface AuditEvent { actor: string; action: string; resource: string;
  result: string; severity: string; ip: string; }
interface SecAuditLogViewerProps { events: AuditEvent[]; total: number;
  bySeverity: Record<string, number>; }

const SEV_COLORS: Record<string, string> = {
  high: "text-red-500", info: "text-blue-400",
};

export function SecAuditLogViewer({ events, total, bySeverity }: SecAuditLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Security Audit Log</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{total} events</span>
          {(bySeverity.high ?? 0) > 0 && <span className="text-red-500">{bySeverity.high} high</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {events.map((e, i) => (
          <div key={i} className="px-4 py-2 text-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={SEV_COLORS[e.severity] ?? ""}>●</span>
                <span className="font-medium">{e.actor}</span>
                <span className="text-gray-400">{e.action}</span>
                <span className="font-mono text-gray-400">{e.resource}</span>
              </div>
              <span className={e.result === "success" ? "text-green-600" : "text-red-500"}>{e.result}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
