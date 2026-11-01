"use client";

interface IdempotencyInfoProps { key: string; isDuplicate: boolean; hasConflict: boolean;
  cachedResponse: Record<string, unknown> | null; originalAt: string | null; }

export function IdempotencyInfo({ key: idemKey, isDuplicate, hasConflict, cachedResponse, originalAt }: IdempotencyInfoProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Idempotency</h3>
        {isDuplicate ? (
          hasConflict ? (
            <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30 dark:text-red-400">Conflict</span>
          ) : (
            <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">Duplicate</span>
          )
        ) : (
          <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">New Request</span>
        )}
      </div>
      <code className="mt-2 block text-xs font-mono text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">{idemKey}</code>
      {isDuplicate && originalAt && <p className="mt-1 text-xs text-gray-400">Original request: {originalAt}</p>}
      {cachedResponse && (
        <pre className="mt-2 rounded bg-gray-100 p-2 text-xs dark:bg-gray-800 overflow-x-auto">{JSON.stringify(cachedResponse, null, 2)}</pre>
      )}
    </div>
  );
}
