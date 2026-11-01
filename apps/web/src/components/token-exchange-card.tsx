"use client";

interface TokenInfo {
  token_prefix: string;
  user_id: string;
  scopes: string[];
  issued_at: string;
  expires_at: string;
  revoked: boolean;
}

interface TokenExchangeCardProps {
  tokens: TokenInfo[];
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

function isExpired(iso: string): boolean {
  return new Date(iso).getTime() < Date.now();
}

export default function TokenExchangeCard({ tokens, appName }: TokenExchangeCardProps) {
  const activeCount = tokens.filter((t) => !t.revoked && !isExpired(t.expires_at)).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Token Exchange</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active tokens</span>
      </div>

      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tokens issued</p>
      ) : (
        <div className="space-y-1.5">
          {tokens.map((t) => {
            const expired = isExpired(t.expires_at);
            const inactive = t.revoked || expired;
            return (
              <div
                key={t.token_prefix}
                className={`flex items-center justify-between rounded px-2.5 py-2 ${inactive ? "opacity-50" : "hover:bg-gray-50 dark:hover:bg-gray-800/50"}`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${inactive ? "bg-gray-300" : "bg-green-500"}`}
                  />
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                        {t.token_prefix}••••
                      </span>
                      <span className="text-[11px] text-gray-400">{t.user_id}</span>
                    </div>
                    <div className="mt-0.5 flex gap-1">
                      {t.scopes.map((s) => (
                        <span
                          key={s}
                          className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="text-[11px] text-gray-400">
                  {t.revoked ? "revoked" : expired ? "expired" : `issued ${timeAgo(t.issued_at)}`}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
