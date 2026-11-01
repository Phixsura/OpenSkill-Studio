"use client";

interface AuditEvent { id: string; keyId: string; action: string; actorId: string; timestamp: string; }
interface Props { events: AuditEvent[]; counts: Record<string, number>; consumerId: string; appName: string; }

const actionColors: Record<string, string> = {
  created: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  rotated: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  revoked: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  scopes_changed: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAuditCard({ events, counts, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Audit Trail</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {Object.keys(counts).length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {Object.entries(counts).map(([action, count]) => (
            <span key={action} className={`rounded px-1.5 py-0.5 text-[9px] ${actionColors[action] ?? "bg-gray-200 text-gray-600"}`}>{action}: {count}</span>
          ))}
        </div>
      )}
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key events</p>
      ) : (
        <div className="space-y-0.5">
          {events.slice(0, 8).map((e) => (
            <div key={e.id} className="flex items-center justify-between text-[10px]">
              <div className="flex items-center gap-1">
                <span className={`rounded px-1 py-0.5 text-[9px] ${actionColors[e.action] ?? "bg-gray-200 text-gray-600"}`}>{e.action}</span>
                <code className="text-gray-500">{e.keyId}</code>
              </div>
              <span className="text-gray-400">{e.actorId} · {e.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
