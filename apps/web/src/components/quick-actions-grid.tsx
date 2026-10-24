"use client";

interface QuickAction { id: string; label: string; icon: string; shortcut?: string; }
interface QuickActionsGridProps { actions: QuickAction[]; onAction: (id: string) => void; }

export function QuickActionsGrid({ actions, onAction }: QuickActionsGridProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">⚡ Quick Actions</h3>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        {actions.map(a => (
          <button key={a.id} onClick={() => onAction(a.id)}
            className="flex flex-col items-center gap-1 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            <span className="text-2xl">{a.icon}</span>
            <span className="text-xs font-medium">{a.label}</span>
            {a.shortcut && <kbd className="text-[10px] text-gray-400 bg-gray-200 dark:bg-gray-700 px-1 rounded">{a.shortcut}</kbd>}
          </button>
        ))}
      </div>
    </div>
  );
}
