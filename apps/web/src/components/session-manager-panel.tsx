"use client";

interface Session { session_hash: string; ip: string; device_type: string;
  user_agent: string; created_at: string; active: boolean; }
interface SessionManagerPanelProps { sessions: Session[]; currentSessionHash: string;
  onRevoke: (hash: string) => void; onRevokeAll: () => void; }

const deviceIcon: Record<string, string> = {
  desktop: "🖥️", mobile: "📱", tablet: "📲", unknown: "❓",
};

export function SessionManagerPanel({ sessions, currentSessionHash, onRevoke, onRevokeAll }: SessionManagerPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Active Sessions</h2>
        <button onClick={onRevokeAll} className="text-xs text-red-500">Revoke All Others</button>
      </div>
      <div className="space-y-2">
        {sessions.map(s => (
          <div key={s.session_hash} className={`flex items-center justify-between rounded-lg border p-3 ${s.session_hash === currentSessionHash ? "border-green-300 dark:border-green-700" : "dark:border-gray-700"}`}>
            <div className="flex items-center gap-3">
              <span className="text-lg">{deviceIcon[s.device_type] ?? "❓"}</span>
              <div>
                <p className="text-sm font-medium">
                  {s.device_type} {s.session_hash === currentSessionHash && <span className="text-xs text-green-500">(current)</span>}
                </p>
                <p className="text-xs text-gray-400">{s.ip} · {new Date(s.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            {s.session_hash !== currentSessionHash && (
              <button onClick={() => onRevoke(s.session_hash)} className="text-xs text-red-500">Revoke</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
