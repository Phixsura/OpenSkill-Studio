"use client";
interface LockInfo { service: string; version: string; lockedBy: string; }
interface DepLockPanelProps { locks: LockInfo[]; }
export function DepLockPanel({ locks }: DepLockPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Dependency Locks</h3>
        <span className="text-xs text-gray-400">{locks.length} locked</span>
      </div>
      {locks.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {locks.map(l => (
            <div key={l.service} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono">{l.service}@{l.version}</span>
              <span className="text-gray-400">by {l.lockedBy}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No locks active</div>
      )}
    </div>
  );
}
