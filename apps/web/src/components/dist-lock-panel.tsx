"use client";

interface LockEntry { resource: string; owner: string; expiresIn: number; }
interface DistLockPanelProps { activeLocks: number; defaultTtl: number; locks: LockEntry[]; }

export function DistLockPanel({ activeLocks, defaultTtl, locks }: DistLockPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Distributed Locks</h3>
        <span className="text-xs text-gray-400">{activeLocks} active · {defaultTtl}s TTL</span>
      </div>
      {locks.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {locks.map(l => (
            <div key={l.resource} className="flex items-center justify-between px-4 py-1.5 text-xs">
              <span className="font-mono">{l.resource}</span>
              <div className="flex items-center gap-2 text-gray-400">
                <span>{l.owner}</span>
                <span>{l.expiresIn}s left</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-gray-400 text-center">No active locks</div>
      )}
    </div>
  );
}
