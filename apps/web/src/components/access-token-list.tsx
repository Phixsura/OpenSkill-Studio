"use client";

interface TokenEntry { name: string; prefix: string; scopes: string[]; revoked: boolean; }
interface AccessTokenListProps { tokens: TokenEntry[]; onCreate: () => void; onRevoke: (prefix: string) => void; }

export function AccessTokenList({ tokens, onCreate, onRevoke }: AccessTokenListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Access Tokens</h3>
        <button onClick={onCreate}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">+ New Token</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tokens.map(t => (
          <div key={t.prefix} className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-400 font-mono">{t.prefix}••••••••</p>
              <div className="flex gap-1 mt-1">
                {t.scopes.map(s => (
                  <span key={s} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{s}</span>
                ))}
              </div>
            </div>
            {t.revoked
              ? <span className="text-xs text-red-500">Revoked</span>
              : <button onClick={() => onRevoke(t.prefix)}
                  className="text-xs px-2 py-1 text-red-600 border border-red-200 rounded hover:bg-red-50">Revoke</button>}
          </div>
        ))}
        {tokens.length === 0 && <p className="p-4 text-sm text-gray-400">No tokens</p>}
      </div>
    </div>
  );
}
