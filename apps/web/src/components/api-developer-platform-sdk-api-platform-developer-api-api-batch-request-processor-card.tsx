"use client";

interface BatchInfo { batch_id: string; item_count: number; success_count: number; error_count: number; total_duration_ms: number; }
interface Props { batches: BatchInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessorCard({ batches, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Processor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {batches.length} batches</p>
      </div>
      {batches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batches processed</p>
      ) : (
        <div className="space-y-1.5">
          {batches.map((b) => (
            <div key={b.batch_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.batch_id} ({b.item_count} items)</span>
              <span className="text-gray-400">✅{b.success_count} ❌{b.error_count} · {Math.round(b.total_duration_ms)}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
