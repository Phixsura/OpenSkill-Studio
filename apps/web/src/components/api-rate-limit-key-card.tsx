"use client";

interface KeyInfo { key_id: string; strategy: string; identifier: string; remaining: number; limit: number; exhausted: boolean; }
interface Props { keys: KeyInfo[]; appName: string; }

export default function APIRateLimitKeyCard({ keys, appName }: Props) {
  const exhausted = keys.filter((k) => k.exhausted).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Rate Limit Keys</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{keys.length} keys</span>
          {exhausted > 0 && <p className="text-[10px] text-red-500">{exhausted} exhausted</p>}
        </div>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limit keys</p>
      ) : (
        <div className="space-y-1">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{k.strategy}</span>
                <span className="text-gray-700 dark:text-gray-300">{k.identifier}</span>
              </div>
              <span className={k.exhausted ? "text-red-500" : "text-gray-400"}>{k.remaining}/{k.limit}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
