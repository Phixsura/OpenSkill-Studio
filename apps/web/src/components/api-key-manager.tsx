"use client";

interface ApiKeyInfo { keyId: string; prefix: string; name: string; scopes: string[]; active: boolean; expiresAt: number; }

export function ApiKeyManager({ keys, onRotate, onRevoke, onCreate }: {
  keys: ApiKeyInfo[]; onRotate?: (keyId: string) => void; onRevoke?: (keyId: string) => void; onCreate?: () => void;
}) {
  const now = Date.now() / 1000;
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">API Keys ({keys.length})</h3>
        <button onClick={onCreate} className="text-xs bg-blue-500 text-white px-3 py-1 rounded-lg">+ New Key</button>
      </div>
      {keys.map(k => {
        const daysLeft = Math.max(0, Math.round((k.expiresAt - now) / 86400));
        return (
          <div key={k.keyId} className="border dark:border-gray-700 rounded-xl p-3">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-sm">{k.name}</span>
                <code className="text-xs text-gray-400 ml-2">{k.prefix}...</code>
              </div>
              <div className="flex gap-1">
                <button onClick={() => onRotate?.(k.keyId)} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">Rotate</button>
                <button onClick={() => onRevoke?.(k.keyId)} className="text-xs text-red-400 px-2 py-1">Revoke</button>
              </div>
            </div>
            <div className="flex gap-2 mt-1">
              {k.scopes.map(s => <span key={s} className="text-[10px] bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{s}</span>)}
              <span className={`text-[10px] ${daysLeft < 7 ? "text-red-500" : "text-gray-400"}`}>{daysLeft}d remaining</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
