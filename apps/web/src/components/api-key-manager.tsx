"use client";

interface ApiKey { prefix: string; name: string; scopes: string[]; created_at: string; revoked: boolean; }
interface ApiKeyManagerProps { keys: ApiKey[]; onRevoke: (prefix: string) => void; }

export function ApiKeyManager({ keys, onRevoke }: ApiKeyManagerProps) {
  const active = keys.filter(k => !k.revoked).length;
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">API Keys</h3>
        <span className="text-xs text-gray-400">{active} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.prefix} className={`flex items-center justify-between py-3 ${k.revoked ? "opacity-50" : ""}`}>
            <div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{k.prefix}••••</code>
                <span className="text-sm">{k.name}</span>
              </div>
              <div className="mt-1 flex gap-1">
                {k.scopes.map(s => (
                  <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{s}</span>
                ))}
              </div>
            </div>
            {!k.revoked && (
              <button onClick={() => onRevoke(k.prefix)} className="text-xs text-red-600 hover:underline">Revoke</button>
            )}
            {k.revoked && <span className="text-xs text-red-500">Revoked</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
