"use client";

interface Token { token_hash: string; scopes: string[]; expires_at: string; client_id: string; }
interface TokenManagerPanelProps { tokens: Token[]; onRevoke: (hash: string) => void; onRefresh: (hash: string) => void; }

export function TokenManagerPanel({ tokens, onRevoke, onRefresh }: TokenManagerPanelProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Active Tokens</h2>
      {tokens.length === 0 ? (
        <p className="text-sm text-gray-400">No active tokens</p>
      ) : (
        <div className="space-y-2">
          {tokens.map(t => {
            const expired = new Date(t.expires_at) < new Date();
            return (
              <div key={t.token_hash} className="rounded-lg border p-3 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-sm">{t.token_hash}••••</p>
                    <p className="text-xs text-gray-400">{t.client_id}</p>
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-xs ${expired ? "bg-red-100 text-red-600 dark:bg-red-900/30" : "bg-green-100 text-green-600 dark:bg-green-900/30"}`}>
                    {expired ? "Expired" : "Active"}
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <div className="flex gap-1">
                    {t.scopes.map(s => (
                      <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{s}</span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => onRefresh(t.token_hash)} className="text-xs text-blue-500">Refresh</button>
                    <button onClick={() => onRevoke(t.token_hash)} className="text-xs text-red-500">Revoke</button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
