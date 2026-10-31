"use client";

interface QuotaResult { action: string; resource: string; usage_pct?: number; remaining?: number;
  overage?: number; message?: string; }
interface QuotaEnforcementBannerProps { results: QuotaResult[]; onUpgrade: () => void; }

export function QuotaEnforcementBanner({ results, onUpgrade }: QuotaEnforcementBannerProps) {
  const blocked = results.filter(r => r.action === "block");
  const warned = results.filter(r => r.action === "warn");
  if (blocked.length === 0 && warned.length === 0) return null;

  return (
    <div className="space-y-2">
      {blocked.map(r => (
        <div key={r.resource} className="flex items-center justify-between rounded-lg border border-red-300 bg-red-50 p-3 dark:border-red-700 dark:bg-red-900/10">
          <div>
            <p className="text-sm font-medium text-red-700 dark:text-red-400">
              🚫 {r.resource} quota exceeded
            </p>
            <p className="text-xs text-red-600 dark:text-red-300">{r.message}</p>
          </div>
          <button onClick={onUpgrade} className="rounded bg-red-600 px-3 py-1 text-xs text-white">Upgrade</button>
        </div>
      ))}
      {warned.map(r => (
        <div key={r.resource} className="flex items-center justify-between rounded-lg border border-yellow-300 bg-yellow-50 p-3 dark:border-yellow-700 dark:bg-yellow-900/10">
          <div>
            <p className="text-sm font-medium text-yellow-700 dark:text-yellow-400">
              ⚠️ {r.resource} approaching limit
            </p>
            <p className="text-xs text-yellow-600 dark:text-yellow-300">{r.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
