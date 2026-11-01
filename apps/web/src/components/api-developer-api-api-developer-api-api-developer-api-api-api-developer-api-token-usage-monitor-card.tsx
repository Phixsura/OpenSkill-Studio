"use client";

interface TokenInfo { token_prefix: string; consumer_id: string; requests_total: number; endpoints_count: number; error_rate: number; }
interface Props { tokens: TokenInfo[]; highErrorCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitorCard({ tokens, highErrorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Token Usage</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {tokens.length} tokens</p>
        </div>
        {highErrorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{highErrorCount} high error</span>}
      </div>
      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No token usage</p>
      ) : (
        <div className="space-y-1.5">
          {tokens.slice(0, 5).map((t) => (
            <div key={t.token_prefix} className="flex items-center justify-between text-[11px]">
              <div>
                <span className="font-mono text-gray-700 dark:text-gray-300">{t.token_prefix}...</span>
                <span className="ml-1 text-[10px] text-gray-400">{t.consumer_id}</span>
              </div>
              <span className="text-gray-400">{t.requests_total.toLocaleString()} reqs · {t.endpoints_count} ep · {t.error_rate}% err</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
