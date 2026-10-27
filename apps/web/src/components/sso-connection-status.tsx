"use client";

interface SSOSession { sessionId: string; extensionId: string; extensionName: string; expiresAt: number; }

export function SSOConnectionStatus({ sessions, onRevoke }: {
  sessions: SSOSession[]; onRevoke?: (sessionId: string) => void;
}) {
  if (!sessions.length) return <div className="text-center text-gray-400 py-6 text-sm">No active SSO sessions</div>;
  const now = Date.now() / 1000;
  return (
    <div className="space-y-2">
      <h3 className="font-bold text-sm">SSO Sessions ({sessions.length})</h3>
      {sessions.map(s => {
        const remaining = Math.max(0, Math.round((s.expiresAt - now) / 60));
        return (
          <div key={s.sessionId} className="flex items-center justify-between border dark:border-gray-700 rounded-xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm font-medium">{s.extensionName}</span>
              <span className="text-xs text-gray-400">{remaining}min remaining</span>
            </div>
            <button onClick={() => onRevoke?.(s.sessionId)} className="text-xs text-red-400">Revoke</button>
          </div>
        );
      })}
    </div>
  );
}
