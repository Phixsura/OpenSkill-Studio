"use client";

interface IdempotencyEntryInfo {
  key: string;
  status_code: number;
  is_expired: boolean;
  ttl_seconds: number;
}

interface IdempotencyStoreCardProps {
  entries: IdempotencyEntryInfo[];
  totalCount: number;
  appName: string;
}

export default function IdempotencyStoreCard({
  entries,
  totalCount,
  appName,
}: IdempotencyStoreCardProps) {
  const active = entries.filter((e) => !e.is_expired).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔁 Idempotency Store
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active} active / {totalCount} total
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No cached keys</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div
              key={e.key}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] text-gray-600 dark:text-gray-400">
                  {e.key}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[10px]">
                <span className={e.status_code < 400 ? "text-green-600" : "text-red-500"}>
                  {e.status_code}
                </span>
                <span className="text-gray-400">{e.ttl_seconds}s</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
