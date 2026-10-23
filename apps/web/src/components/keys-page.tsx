"use client";

interface ApiKey { prefix: string; name: string; scopes: string[];
  revoked: boolean; requests30d: number; lastUsed: string | null; }
interface KeysPageProps { appName: string; keys: ApiKey[]; active: number;
  totalRequests30d: number; canCreate: boolean;
  onRevoke: (prefix: string) => void; onCreate: () => void; }

export function KeysPage({ appName, keys, active, totalRequests30d, canCreate,
  onRevoke, onCreate }: KeysPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔑 {appName} — API Keys</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{active} active · {totalRequests30d.toLocaleString()} req/30d</span>
          {canCreate && <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ New Key</button>}
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {keys.map(k => (
          <div key={k.prefix} className={`px-4 py-3 ${k.revoked ? "opacity-40" : ""}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{k.prefix}••••</code>
                  <span className="text-sm">{k.name}</span>
                  {k.revoked && <span className="text-xs text-red-500">Revoked</span>}
                </div>
                <div className="mt-1 flex gap-1">
                  {k.scopes.map(s => <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{s}</span>)}
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">{k.requests30d.toLocaleString()} req</p>
                {!k.revoked && <button onClick={() => onRevoke(k.prefix)} className="text-xs text-red-600 hover:underline">Revoke</button>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
