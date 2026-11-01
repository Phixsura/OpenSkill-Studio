"use client";

interface QuickAction { id: string; label: string; icon: string; category: string; shortcut: string; }
interface QuickActionLauncherProps { actions: QuickAction[]; onExecute: (id: string) => void; }

export function QuickActionLauncher({ actions, onExecute }: QuickActionLauncherProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Quick Actions</h3>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-3">
        {actions.map(a => (
          <button key={a.id} onClick={() => onExecute(a.id)}
            className="flex flex-col items-center p-3 rounded-lg border dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
            <span className="text-2xl mb-1">{a.icon}</span>
            <span className="text-xs font-medium">{a.label}</span>
            <kbd className="text-[10px] text-gray-400 mt-0.5">{a.shortcut}</kbd>
          </button>
        ))}
      </div>
    </div>
  );
}
