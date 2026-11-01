"use client";

interface QuickAction {
  actionId: string; name: string; icon: string;
  dangerous: boolean; requiresConfirm: boolean; executionCount: number;
}

export function QuickActionBar({ actions, onExecute }: {
  actions: QuickAction[]; onExecute?: (actionId: string) => void;
}) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">⚡ Quick Actions</h2>
      <div className="flex gap-2 flex-wrap">
        {actions.map((a) => (
          <button key={a.actionId} onClick={() => onExecute?.(a.actionId)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl border text-sm font-medium transition hover:shadow ${
              a.dangerous ? "border-red-300 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/10" : "dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            }`}>
            <span className="text-lg">{a.icon}</span>
            <span>{a.name}</span>
            {a.executionCount > 0 && <span className="text-xs text-gray-400">×{a.executionCount}</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
