"use client";

interface LockInfo {
  resource: string;
  owner: string;
  acquired_at: string;
  expires_in_seconds: number;
}

interface ResourceLockCardProps {
  locks: LockInfo[];
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3_600_000)}h ago`;
}

export default function ResourceLockCard({ locks, appName }: ResourceLockCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Resource Locks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            locks.length > 0
              ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
              : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
          }`}
        >
          {locks.length > 0 ? `${locks.length} active` : "None held"}
        </span>
      </div>

      {locks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active locks</p>
      ) : (
        <div className="space-y-2">
          {locks.map((l) => (
            <div
              key={l.resource}
              className="flex items-center justify-between rounded-lg border border-yellow-200 bg-yellow-50/50 px-3 py-2 dark:border-yellow-900/50 dark:bg-yellow-950/20"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    🔒 {l.resource}
                  </span>
                </div>
                <div className="mt-0.5 text-[11px] text-gray-400">
                  Held by {l.owner} · acquired {timeAgo(l.acquired_at)}
                </div>
              </div>
              <span className="text-[11px] text-yellow-600 dark:text-yellow-400">
                expires in {l.expires_in_seconds}s
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
