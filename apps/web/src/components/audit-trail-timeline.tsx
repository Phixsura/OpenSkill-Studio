"use client";

interface AuditEvent { seq: number; actor: string; action: string;
  resource: string; detail: string; hash: string; }
interface AuditTrailTimelineProps { events: AuditEvent[]; total: number; }

const ACTION_ICONS: Record<string, string> = {
  create: "🟢", update: "🟡", delete: "🔴", deploy: "🚀", login: "🔑",
};

export function AuditTrailTimeline({ events, total }: AuditTrailTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Audit Trail</h3>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map(e => (
          <div key={e.seq} className="px-4 py-2.5 flex items-start gap-3">
            <span className="text-lg mt-0.5">{ACTION_ICONS[e.action] ?? "⚪"}</span>
            <div className="flex-1 min-w-0">
              <div className="text-sm">
                <span className="font-medium">{e.actor}</span>{" "}
                <span className="text-gray-400">{e.action}</span>{" "}
                <span className="font-mono text-xs">{e.resource}</span>
              </div>
              {e.detail && <div className="text-xs text-gray-400 mt-0.5">{e.detail}</div>}
            </div>
            <span className="text-[10px] text-gray-300 font-mono">#{e.seq}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
