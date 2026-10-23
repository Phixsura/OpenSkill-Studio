"use client";

interface LockEntry { resource: string; owner: string; ttlRemaining: number; }
interface DistLockPanelProps { locks: LockEntry[]; onRelease: (resource: string) => void; }

export function DistLockPanel({ locks, onRelease }: DistLockPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Distributed Locks</h3>
        <span className="text-xs text-gray-400">{locks.length} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {locks.map(l => (
          <div key={l.resource} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-mono">{l.resource}</div>
              <div className="text-[10px] text-gray-400">held by {l.owner} · {l.ttlRemaining}s remaining</div>
            </div>
            <button onClick={() => onRelease(l.resource)}
              className="text-xs text-red-500 hover:underline">Force Release</button>
          </div>
        ))}
        {locks.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No active locks</div>}
      </div>
    </div>
  );
}
