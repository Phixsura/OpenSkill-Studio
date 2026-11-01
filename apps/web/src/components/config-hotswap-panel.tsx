"use client";

interface ConfigHotswapPanelProps { activeHash: string | null; pendingHash: string | null;
  activeKeyCount: number; hasPending: boolean;
  onActivate: () => void; onRollback: () => void; }

export function ConfigHotswapPanel({ activeHash, pendingHash, activeKeyCount, hasPending, onActivate, onRollback }: ConfigHotswapPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Config Hot-Swap</h3>
        <span className="text-xs text-gray-400">{activeKeyCount} keys · {activeHash ?? "none"}</span>
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span>Active: <span className="font-mono">{activeHash ?? "—"}</span></span>
          <button onClick={onRollback} className="text-xs text-yellow-600 hover:underline">Rollback</button>
        </div>
        {hasPending && (
          <div className="flex items-center justify-between p-2 bg-blue-50 dark:bg-blue-900/10 rounded">
            <span className="text-xs">Pending: <span className="font-mono">{pendingHash}</span></span>
            <button onClick={onActivate} className="px-2 py-1 text-xs bg-green-500 text-white rounded">Activate</button>
          </div>
        )}
      </div>
    </div>
  );
}
