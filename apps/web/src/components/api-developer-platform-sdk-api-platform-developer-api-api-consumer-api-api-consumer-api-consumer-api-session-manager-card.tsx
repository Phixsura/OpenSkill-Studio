"use client";

interface Session { id: string; ip: string; userAgent: string; lastActive: string; created: string; }
interface Props { sessions: Session[]; consumerId: string; maxSessions: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManagerCard({ sessions, consumerId, maxSessions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Active Sessions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {sessions.length}/{maxSessions} sessions</p>
      </div>
      {sessions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active sessions</p>
      ) : (
        <div className="space-y-1">
          {sessions.map((s) => (
            <div key={s.id} className="rounded bg-gray-50 px-2 py-1.5 text-[10px] dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <code className="text-gray-600 dark:text-gray-400">{s.id}</code>
                <span className="text-gray-400">{s.lastActive}</span>
              </div>
              <div className="text-gray-400">{s.ip}{s.userAgent && ` · ${s.userAgent}`}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
