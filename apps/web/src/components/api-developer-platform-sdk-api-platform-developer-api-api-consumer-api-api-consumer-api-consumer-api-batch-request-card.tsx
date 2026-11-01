"use client";

interface Result { itemId: string; method: string; path: string; status: number; error: string | null; }
interface Props { results: Result[]; total: number; succeeded: number; failed: number; totalBatches: number; totalItems: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequestCard({ results, total, succeeded, failed, totalBatches, totalItems, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Requests</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {totalBatches} batches · {totalItems} total items</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{total}</div><div className="text-[10px] text-gray-400">Total</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{succeeded}</div><div className="text-[10px] text-gray-400">OK</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{failed}</div><div className="text-[10px] text-gray-400">Failed</div></div>
      </div>
      {results.length > 0 && (
        <div className="space-y-1">
          {results.slice(0, 6).map((r) => (
            <div key={r.itemId} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex gap-1"><span className="font-bold text-blue-600">{r.method}</span><code className="text-gray-500">{r.path}</code></div>
              <span className={r.status < 400 ? "text-green-500" : "text-red-500"}>{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
