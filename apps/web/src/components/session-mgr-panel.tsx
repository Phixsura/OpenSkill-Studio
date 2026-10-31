"use client";

interface SessionInfo { userId: string; remaining: number; }
interface SessionMgrPanelProps { sessions: SessionInfo[]; activeSessions: number; ttlSeconds: number; }

export function SessionMgrPanel({ sessions, activeSessions, ttlSeconds }: SessionMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👤 Sessions</h3>
        <span className="text-xs text-gray-400">{activeSessions} active · {ttlSeconds}s TTL</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {sessions.map((s, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.userId}</span>
            <span className="text-gray-400">{s.remaining}s left</span>
          </div>
        ))}
      </div>
    </div>
  );
}
