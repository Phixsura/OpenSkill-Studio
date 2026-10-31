"use client";

interface TokenInfo { token_id: string; consumer_id: string; scopes: string[]; expires_in_min: number; revoked: boolean; }
interface Props { tokens: TokenInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManagerCard({ tokens, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎟️ Access Tokens</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{activeCount} active</span>
      </div>
      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tokens issued</p>
      ) : (
        <div className="space-y-1.5">
          {tokens.map((t) => (
            <div key={t.token_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{t.consumer_id}</span>
                <span className={t.revoked ? "text-red-500" : "text-green-600 dark:text-green-400"}>{t.revoked ? "revoked" : `${t.expires_in_min}m left`}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {t.scopes.map((s) => <span key={s} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{s}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
