"use client";

interface RollbackOption { version: string; deployedAt: string; commit: string; author: string; }
interface RollbackPanelProps { current: string; options: RollbackOption[]; canRollback: boolean;
  onRollback: (version: string) => void; }

export function RollbackPanel({ current, options, canRollback, onRollback }: RollbackPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Rollback</h3>
        <span className="text-xs text-gray-400">Current: v{current}</span>
      </div>
      {!canRollback && <p className="text-sm text-gray-400">No previous versions available</p>}
      <div className="space-y-2">
        {options.map(o => (
          <div key={o.version} className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold">v{o.version}</span>
                <code className="text-xs text-gray-400">{o.commit}</code>
              </div>
              <p className="text-xs text-gray-400">by {o.author} · {o.deployedAt}</p>
            </div>
            <button onClick={() => onRollback(o.version)}
              className="rounded border border-red-300 px-3 py-1 text-xs text-red-600 hover:bg-red-50 dark:border-red-700 dark:hover:bg-red-900/10">
              Rollback
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
