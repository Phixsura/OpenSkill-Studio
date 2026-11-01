"use client";

interface SessionInfo { session_id: string; consumer_id: string; request_count: number; endpoints_count: number; active: boolean; }
interface Props { sessions: SessionInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiConsumerSessionTrackerCard({ sessions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Active Sessions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">{activeCount} active</span>
      </div>
      {sessions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sessions</p>
      ) : (
        <div className="space-y-1">
          {sessions.slice(0, 5).map((s) => (
            <div key={s.session_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${s.active ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              </div>
              <span className="text-gray-400">{s.request_count} reqs · {s.endpoints_count} ep</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
