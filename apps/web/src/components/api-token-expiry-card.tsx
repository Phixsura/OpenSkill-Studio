"use client";

interface TokenExpiryInfo {
  token_id: string;
  label: string;
  days_remaining: number;
  is_expired: boolean;
}

interface APITokenExpiryCardProps {
  tokens: TokenExpiryInfo[];
  appName: string;
}

export default function APITokenExpiryCard({ tokens, appName }: APITokenExpiryCardProps) {
  const expired = tokens.filter((t) => t.is_expired).length;
  const expiring = tokens.filter((t) => !t.is_expired && t.days_remaining <= 30).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Token Expiry</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right text-[10px]">
          {expired > 0 && <p className="text-red-500">{expired} expired</p>}
          {expiring > 0 && <p className="text-yellow-600">{expiring} expiring soon</p>}
        </div>
      </div>

      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tokens tracked</p>
      ) : (
        <div className="space-y-1">
          {tokens.map((t) => (
            <div key={t.token_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{t.label}</span>
              <span className={t.is_expired ? "text-red-500" : t.days_remaining <= 30 ? "text-yellow-600" : "text-gray-400"}>
                {t.is_expired ? "expired" : `${t.days_remaining}d left`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
