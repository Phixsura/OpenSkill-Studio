"use client";

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  description: string;
  shortcut?: string;
  disabled?: boolean;
  danger?: boolean;
}

export function ExtensionQuickActions({
  extensionName,
  actions,
  onAction,
}: {
  extensionName: string;
  actions: QuickAction[];
  onAction?: (actionId: string) => void;
}) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-gray-500">⚡ Quick Actions — {extensionName}</h3>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => !action.disabled && onAction?.(action.id)}
            disabled={action.disabled}
            className={`text-left rounded-lg border p-3 transition ${
              action.disabled
                ? "opacity-40 cursor-not-allowed border-gray-200 dark:border-gray-700"
                : action.danger
                  ? "border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/10"
                  : "border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-lg">{action.icon}</span>
              {action.shortcut && (
                <kbd className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded font-mono">
                  {action.shortcut}
                </kbd>
              )}
            </div>
            <div className={`text-sm font-medium mt-1 ${action.danger ? "text-red-600 dark:text-red-400" : ""}`}>
              {action.label}
            </div>
            <div className="text-xs text-gray-400 mt-0.5">{action.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
