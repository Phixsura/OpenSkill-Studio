"use client";

interface TokenInfo { token_id: string; name: string; developer_id: string; scopes: string[]; is_active: boolean; use_count: number; revoked: boolean; }
interface Props { tokens: TokenInfo[]; appName: string; }

export default function APIDeveloperAPIAccessTokenManagerCard({ tokens, appName }: Props) {
  const active = tokens.filter((t) => t.is_active).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎫 Access Tokens</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{tokens.length} active</span>
      </div>
      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No access tokens</p>
      ) : (
        <div className="space-y-1.5">
          {tokens.map((t) => (
            <div key={t.token_id} className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${!t.is_active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{t.name}</span>
                <span className="text-gray-400">{t.use_count} uses{t.revoked ? " · revoked" : ""}</span>
              </div>
              {t.scopes.length > 0 && (
                <div className="mt-0.5 flex gap-1">
                  {t.scopes.map((s) => <span key={s} className="rounded bg-gray-100 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-800">{s}</span>)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
