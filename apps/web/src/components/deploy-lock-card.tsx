"use client";

interface DeployLockInfo {
  lock_id: string;
  owner: string;
  reason: string;
  is_active: boolean;
  is_expired: boolean;
}

interface DeployLockCardProps {
  currentLock: DeployLockInfo | null;
  history: DeployLockInfo[];
  appName: string;
}

export default function DeployLockCard({ currentLock, history, appName }: DeployLockCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Deploy Lock</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span
          className={`rounded px-2 py-0.5 text-[11px] font-medium ${
            currentLock
              ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
              : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
          }`}
        >
          {currentLock ? "Locked" : "Unlocked"}
        </span>
      </div>

      {currentLock && (
        <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 dark:bg-red-900/20">
          <p className="text-xs font-medium text-red-700 dark:text-red-300">
            Locked by {currentLock.owner}
          </p>
          {currentLock.reason && <p className="text-[10px] text-red-500">{currentLock.reason}</p>}
        </div>
      )}

      {history.length > 0 && (
        <div className="space-y-1">
          <p className="text-[10px] text-gray-500">Recent locks</p>
          {history.slice(0, 5).map((l) => (
            <div key={l.lock_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-600 dark:text-gray-400">{l.owner}</span>
              <span className="text-gray-400">
                {l.is_active ? "active" : l.is_expired ? "expired" : "released"}
              </span>
            </div>
          ))}
        </div>
      )}

      {!currentLock && history.length === 0 && (
        <p className="text-center text-sm text-gray-400">No deploy locks</p>
      )}
    </div>
  );
}
