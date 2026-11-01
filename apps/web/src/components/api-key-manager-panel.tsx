"use client";

interface ApiKey { name: string; prefix: string; scopes: string[]; revoked: boolean; }
interface ApiKeyManagerPanelProps { keys: ApiKey[]; onCreate: () => void; onRevoke: (prefix: string) => void; }

export function ApiKeyManagerPanel({ keys, onCreate, onRevoke }: ApiKeyManagerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 API Keys</h3>
        <button onClick={onCreate} className="px-3 py-1 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600">New Key</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.prefix} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="text-sm font-medium">{k.name}</div>
              <div className="text-xs text-gray-400">
                <span className="font-mono">{k.prefix}...</span>
                <span className="ml-2">{k.scopes.join(", ")}</span>
              </div>
            </div>
            {k.revoked ? (
              <span className="text-xs text-red-500">Revoked</span>
            ) : (
              <button onClick={() => onRevoke(k.prefix)}
                className="text-xs text-red-500 hover:underline">Revoke</button>
            )}
          </div>
        ))}
        {keys.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No API keys</div>}
      </div>
    </div>
  );
}
