"use client";

interface AuditInfo { event_id: string; actor_id: string; actor_type: string; action: string; resource_type: string; }
interface Props { events: AuditInfo[]; totalCount: number; securityEventCount: number; appName: string; }

const actorIcon: Record<string, string> = { consumer: "👤", admin: "👑", system: "🤖", api_key: "🔑" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrailCard({ events, totalCount, securityEventCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Audit Trail</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalCount.toLocaleString()} events</p>
        </div>
        {securityEventCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">🛡️ {securityEventCount} security</span>}
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit events</p>
      ) : (
        <div className="space-y-1">
          {events.map((e) => (
            <div key={e.event_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{actorIcon[e.actor_type] ?? "•"}</span>
                <span className="text-gray-500">{e.actor_id}</span>
              </div>
              <span className="text-gray-400">{e.action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
