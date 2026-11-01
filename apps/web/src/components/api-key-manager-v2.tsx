"use client";

interface ApiKey { name: string; prefix: string; scopes: string[]; expires_at: string | null; usage_count: number; }
interface ApiKeyManagerV2Props { keys: ApiKey[]; onCreate: () => void; onRevoke: (prefix: string) => void; }

export function ApiKeyManagerV2({ keys, onCreate, onRevoke }: ApiKeyManagerV2Props) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">API Keys</h3>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ New Key</button>
      </div>
      {keys.length === 0 ? <p className="mt-3 text-sm text-gray-400">No API keys created.</p> : (
        <ul className="mt-3 space-y-2">
          {keys.map(k => (
            <li key={k.prefix} className="flex items-center justify-between rounded border p-2 dark:border-gray-700">
              <div>
                <p className="text-sm font-medium">{k.name}</p>
                <p className="text-xs text-gray-400">
                  <code>{k.prefix}•••</code> · {k.scopes.join(", ")} · {k.usage_count.toLocaleString()} uses
                </p>
                {k.expires_at && <p className="text-xs text-yellow-600">Expires: {k.expires_at.slice(0, 10)}</p>}
              </div>
              <button onClick={() => onRevoke(k.prefix)} className="rounded border px-2 py-1 text-xs text-red-600">Revoke</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
