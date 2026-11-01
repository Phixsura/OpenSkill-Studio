"use client";

interface ApiKey { prefix: string; name: string; scopes: string[]; createdAt: string;
  lastUsed: string | null; revoked: boolean; requests30d: number; }
interface ApiKeyListPageProps { keys: ApiKey[]; active: number; onRevoke: (prefix: string) => void;
  onCreateNew: () => void; }

export function ApiKeyListPage({ keys, active, onRevoke, onCreateNew }: ApiKeyListPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔑 API Keys</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{active} active</span>
          <button onClick={onCreateNew} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ New Key</button>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {keys.map(k => (
          <div key={k.prefix} className={`px-4 py-3 ${k.revoked ? "opacity-40" : ""}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{k.prefix}••••</code>
                  <span className="text-sm font-medium">{k.name}</span>
                  {k.revoked && <span className="text-xs text-red-500">Revoked</span>}
                </div>
                <div className="mt-1 flex gap-1">
                  {k.scopes.map(s => <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{s}</span>)}
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">{k.requests30d.toLocaleString()} req/30d</p>
                {!k.revoked && <button onClick={() => onRevoke(k.prefix)} className="text-xs text-red-600 hover:underline">Revoke</button>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
