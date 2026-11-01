"use client";

interface LockInfo { key: string; owner: string; }
interface DistLocksPanelProps { locks: LockInfo[]; activeLocks: number;
  onRelease: (key: string) => void; }

export function DistLocksPanel({ locks, activeLocks, onRelease }: DistLocksPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔒 Distributed Locks</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${activeLocks > 0 ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
          {activeLocks} active
        </span>
      </div>
      <div className="space-y-2">
        {locks.map(l => (
          <div key={l.key} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div>
              <span className="text-sm font-mono">{l.key}</span>
              <span className="text-xs text-gray-400 ml-2">by {l.owner}</span>
            </div>
            <button onClick={() => onRelease(l.key)}
              className="text-xs px-2 py-1 border border-red-200 text-red-600 rounded hover:bg-red-50">Force Release</button>
          </div>
        ))}
        {locks.length === 0 && <p className="text-sm text-gray-400 text-center">No active locks</p>}
      </div>
    </div>
  );
}
