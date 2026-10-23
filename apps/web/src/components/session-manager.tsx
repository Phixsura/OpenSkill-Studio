"use client";

interface Session { device: string; ip: string; created_at: string; active: boolean; is_current: boolean; }
interface SessionManagerProps { sessions: Session[]; onRevoke: (idx: number) => void; }

export function SessionManager({ sessions, onRevoke }: SessionManagerProps) {
  const active = sessions.filter(s => s.active).length;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Active Sessions</h3>
        <span className="text-xs text-gray-400">{active} active</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {sessions.map((s, i) => (
          <div key={i} className={`flex items-center justify-between px-4 py-3 ${!s.active ? "opacity-40" : ""}`}>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{s.device}</span>
                {s.is_current && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">Current</span>}
              </div>
              <p className="text-xs text-gray-400">{s.ip} · {new Date(s.created_at).toLocaleDateString()}</p>
            </div>
            {s.active && !s.is_current && (
              <button onClick={() => onRevoke(i)} className="text-xs text-red-600 hover:underline">Revoke</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
