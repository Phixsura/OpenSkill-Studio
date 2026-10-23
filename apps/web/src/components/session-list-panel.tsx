"use client";

interface SessionInfo { id: string; ip: string; userAgent: string; }
interface SessionListPanelProps { sessions: SessionInfo[]; currentSessionId: string;
  onRevoke: (id: string) => void; }

export function SessionListPanel({ sessions, currentSessionId, onRevoke }: SessionListPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🖥️ Active Sessions</h3>
      <div className="space-y-2">
        {sessions.map(s => (
          <div key={s.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono text-xs">{s.id.slice(0, 16)}…</span>
                {s.id === currentSessionId && <span className="text-xs text-green-600">Current</span>}
              </div>
              <p className="text-xs text-gray-400">{s.ip} · {s.userAgent}</p>
            </div>
            {s.id !== currentSessionId && (
              <button onClick={() => onRevoke(s.id)}
                className="text-xs px-2 py-1 text-red-500 border border-red-200 rounded hover:bg-red-50">Revoke</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
