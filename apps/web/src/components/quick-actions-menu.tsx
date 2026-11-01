"use client";

import { useState } from "react";

interface Action { id: string; label: string; icon: string; danger?: boolean; primary?: boolean; url?: string; }
interface QuickActionsMenuProps { actions: Action[]; onAction: (id: string) => void; }

export function QuickActionsMenu({ actions, onAction }: QuickActionsMenuProps) {
  const [open, setOpen] = useState(false);
  const primaryAction = actions.find(a => a.primary);
  const menuActions = actions.filter(a => !a.primary);

  return (
    <div className="relative flex gap-2">
      {primaryAction && (
        <button onClick={() => onAction(primaryAction.id)}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700">
          {primaryAction.icon} {primaryAction.label}
        </button>
      )}
      <button onClick={() => setOpen(!open)} className="rounded border px-2 py-1.5 text-sm hover:bg-gray-50 dark:border-gray-700">⋮</button>
      {open && (
        <div className="absolute right-0 top-10 z-50 w-48 rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          {menuActions.map(a => (
            <button key={a.id} onClick={() => { onAction(a.id); setOpen(false); }}
              className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 ${a.danger ? "text-red-600" : ""}`}>
              <span>{a.icon}</span>{a.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
