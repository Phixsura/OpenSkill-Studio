"use client";

interface SessionInfo {
  session_id: string;
  user_id: string;
  is_active: boolean;
  ip_address: string;
  user_agent: string;
}

interface SessionManagerCardProps {
  sessions: SessionInfo[];
  activeCount: number;
  appName: string;
}

export default function SessionManagerCard({
  sessions,
  activeCount,
  appName,
}: SessionManagerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👤 Sessions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {activeCount} active / {sessions.length} total
        </span>
      </div>

      {sessions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sessions</p>
      ) : (
        <div className="space-y-1.5">
          {sessions.map((s) => (
            <div
              key={s.session_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${s.is_active ? "bg-green-500" : "bg-gray-400"}`}
                />
                <span className="text-xs text-gray-700 dark:text-gray-300">{s.user_id}</span>
              </div>
              <div className="text-right text-[10px] text-gray-400">
                {s.ip_address && <span>{s.ip_address}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
