"use client";

interface SessionInfo {
  session_id: string;
  user_id: string;
  created_at: string;
  expires_at: string;
  last_accessed_at: string;
  revoked: boolean;
  data_keys: string[];
}

interface SessionStoreCardProps {
  sessions: SessionInfo[];
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

function isExpired(expiresAt: string): boolean {
  return new Date(expiresAt).getTime() < Date.now();
}

export default function SessionStoreCard({ sessions, appName }: SessionStoreCardProps) {
  const activeCount = sessions.filter((s) => !s.revoked && !isExpired(s.expires_at)).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Sessions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {sessions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sessions</p>
      ) : (
        <div className="space-y-2">
          {sessions.map((s) => {
            const expired = isExpired(s.expires_at);
            const inactive = s.revoked || expired;
            return (
              <div
                key={s.session_id}
                className={`rounded-lg border px-3 py-2 ${
                  inactive
                    ? "border-gray-100 opacity-50 dark:border-gray-800"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-2 w-2 rounded-full ${inactive ? "bg-gray-300 dark:bg-gray-600" : "bg-green-500"}`}
                    />
                    <span className="text-sm text-gray-800 dark:text-gray-200">{s.user_id}</span>
                    {s.revoked && <span className="text-[10px] text-red-500">revoked</span>}
                    {expired && !s.revoked && (
                      <span className="text-[10px] text-yellow-500">expired</span>
                    )}
                  </div>
                  <span className="font-mono text-[10px] text-gray-400">{s.session_id}</span>
                </div>
                <div className="mt-1 flex items-center gap-3 text-[11px] text-gray-400">
                  <span>Last active {timeAgo(s.last_accessed_at)}</span>
                  {s.data_keys.length > 0 && <span>· {s.data_keys.length} data keys</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
