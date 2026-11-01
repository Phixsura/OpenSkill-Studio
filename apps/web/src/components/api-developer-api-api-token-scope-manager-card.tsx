"use client";

interface TokenInfo { token_id: string; name: string; scopes: string[]; revoked: boolean; }
interface Props { tokens: TokenInfo[]; appName: string; }

export default function APIDeveloperAPIApiTokenScopeManagerCard({ tokens, appName }: Props) {
  const activeCount = tokens.filter(t => !t.revoked).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Token Scopes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active tokens</p>
      </div>
      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tokens</p>
      ) : (
        <div className="space-y-2">
          {tokens.map((t) => (
            <div key={t.token_id} className={`rounded-lg px-3 py-2 ${t.revoked ? "bg-red-50 dark:bg-red-900/20 opacity-60" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
                {t.revoked && <span className="text-[9px] text-red-500 font-bold">REVOKED</span>}
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {t.scopes.map((s) => (
                  <span key={s} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{s}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
