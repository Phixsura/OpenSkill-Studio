"use client";

interface SessionInfo {
  session_id: string;
  user_id: string;
  request_count: number;
  active: boolean;
}

interface APIPlaygroundSessionCardProps {
  sessions: SessionInfo[];
  appName: string;
}

export default function APIPlaygroundSessionCard({ sessions, appName }: APIPlaygroundSessionCardProps) {
  const active = sessions.filter((s) => s.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎮 Playground Sessions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active} active / {sessions.length} total</span>
      </div>

      {sessions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sessions</p>
      ) : (
        <div className="space-y-1">
          {sessions.map((s) => (
            <div key={s.session_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${s.active ? "bg-green-500" : "bg-gray-400"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{s.user_id}</span>
              </div>
              <span className="text-[10px] text-gray-400">{s.request_count} reqs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
