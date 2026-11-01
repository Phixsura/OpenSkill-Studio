"use client";

interface Snapshot { version: string; status: string; }
interface RollbackChange { key: string; from: unknown; to: unknown; }
interface RollbackControlPanelProps { snapshots: Snapshot[]; currentVersion: string;
  lastRollback: { fromVersion: string; toVersion: string; changes: RollbackChange[] } | null;
  onRollback: (version: string) => void; }

export function RollbackControlPanel({ snapshots, currentVersion, lastRollback, onRollback }: RollbackControlPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏪ Rollback Control</h3>
        <span className="text-xs text-gray-400">Current: v{currentVersion}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {snapshots.map(s => (
          <div key={s.version} className="flex items-center justify-between px-4 py-2.5">
            <span className="text-sm font-mono">v{s.version}</span>
            {s.version !== currentVersion ? (
              <button onClick={() => onRollback(s.version)}
                className="px-2 py-1 text-xs bg-yellow-500 text-white rounded">⏪ Rollback</button>
            ) : (
              <span className="text-xs text-green-600">● Current</span>
            )}
          </div>
        ))}
      </div>
      {lastRollback && (
        <div className="p-3 border-t dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/10">
          <div className="text-xs text-yellow-700">Last rollback: v{lastRollback.fromVersion} → v{lastRollback.toVersion} ({lastRollback.changes.length} changes)</div>
        </div>
      )}
    </div>
  );
}
