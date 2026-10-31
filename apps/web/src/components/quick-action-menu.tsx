"use client";

interface Action { id: string; label: string; icon: string; shortcut: string | null; danger: boolean; }
interface QuickActionMenuProps { actions: Action[]; onAction: (id: string) => void; onClose: () => void; }

export function QuickActionMenu({ actions, onAction, onClose }: QuickActionMenuProps) {
  return (
    <div className="absolute right-0 z-20 mt-1 w-48 rounded-lg border bg-white shadow-xl dark:bg-gray-900 dark:border-gray-700" onClick={e => e.stopPropagation()}>
      {actions.map((a, i) => (
        <button key={a.id} onClick={() => { onAction(a.id); onClose(); }}
          className={`flex w-full items-center justify-between px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 ${a.danger ? "text-red-600" : ""} ${i === 0 ? "rounded-t-lg" : ""} ${i === actions.length - 1 ? "rounded-b-lg" : ""}`}>
          <div className="flex items-center gap-2">
            <span className="text-xs">{a.icon}</span>
            <span>{a.label}</span>
          </div>
          {a.shortcut && <kbd className="text-xs text-gray-400">{a.shortcut}</kbd>}
        </button>
      ))}
    </div>
  );
}
