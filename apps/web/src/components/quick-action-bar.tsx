"use client";

interface Action { id: string; label: string; icon: string; danger: boolean; confirm: boolean; }
interface QuickActionBarProps { actions: Action[]; onExecute: (id: string) => void; }

export function QuickActionBar({ actions, onExecute }: QuickActionBarProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {actions.map(a => (
        <button key={a.id} onClick={() => onExecute(a.id)}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-sm ${a.danger ? "border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/10" : "hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"}`}>
          <span>{a.icon}</span>
          <span>{a.label}</span>
        </button>
      ))}
    </div>
  );
}
