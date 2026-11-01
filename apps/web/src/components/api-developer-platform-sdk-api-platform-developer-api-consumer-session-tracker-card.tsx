"use client";

interface SessionInfo { session_id: string; consumer_id: string; request_count: number; idle_minutes: number; }
interface Props { sessions: SessionInfo[]; uniqueConsumers: number; idleCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTrackerCard({ sessions, uniqueConsumers, idleCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Active Sessions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {idleCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">💤 {idleCount} idle</span>}
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{sessions.length}</div><div className="text-gray-400">Sessions</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{uniqueConsumers}</div><div className="text-gray-400">Consumers</div></div>
      </div>
      {sessions.length > 0 && (
        <div className="space-y-1">
          {sessions.slice(0, 5).map((s) => (
            <div key={s.session_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className="text-gray-400">{s.request_count} reqs · {s.idle_minutes}m idle</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
