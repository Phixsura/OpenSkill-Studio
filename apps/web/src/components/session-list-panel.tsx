"use client";

interface Session { sessionId: string; ip: string; userAgent: string; active: boolean; }
interface SessionListPanelProps { sessions: Session[]; activeCount: number;
  uniqueUsers: number; onRevoke: (id: string) => void; }

export function SessionListPanel({ sessions, activeCount, uniqueUsers, onRevoke }: SessionListPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👤 Active Sessions</h3>
        <span className="text-xs text-gray-400">{activeCount} sessions · {uniqueUsers} users</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {sessions.map(s => (
          <div key={s.sessionId} className={`flex items-center justify-between px-4 py-2.5 ${!s.active ? "opacity-50" : ""}`}>
            <div>
              <div className="text-xs font-mono">{s.sessionId}</div>
              <div className="text-[10px] text-gray-400">{s.ip} · {s.userAgent || "Unknown"}</div>
            </div>
            {s.active ? (
              <button onClick={() => onRevoke(s.sessionId)} className="text-xs text-red-500 hover:underline">Revoke</button>
            ) : (
              <span className="text-xs text-gray-400">Revoked</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
