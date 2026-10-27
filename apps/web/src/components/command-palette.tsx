"use client";
import { useState } from "react";

interface Command { commandId: string; label: string; category: string; shortcut: string; icon: string; handler: string; }

export function CommandPalette({ commands, open, onClose, onExecute }: {
  commands: Command[]; open: boolean; onClose?: () => void; onExecute?: (handler: string) => void;
}) {
  const [query, setQuery] = useState("");
  const filtered = query ? commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase())) : commands;
  const grouped = filtered.reduce((acc, c) => { (acc[c.category] = acc[c.category] || []).push(c); return acc; }, {} as Record<string, Command[]>);

  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-24 z-50" onClick={onClose}>
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-lg border dark:border-gray-700" onClick={e => e.stopPropagation()}>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Type a command..."
          className="w-full px-4 py-3 text-sm bg-transparent border-b dark:border-gray-700 outline-none" autoFocus />
        <div className="max-h-72 overflow-y-auto p-2">
          {Object.entries(grouped).map(([cat, cmds]) => (
            <div key={cat}>
              <span className="text-[10px] uppercase text-gray-400 px-2 py-1 block">{cat}</span>
              {cmds.map(c => (
                <button key={c.commandId} onClick={() => { onExecute?.(c.handler); onClose?.(); }}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                  </div>
                  {c.shortcut && <kbd className="text-[10px] bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{c.shortcut}</kbd>}
                </button>
              ))}
            </div>
          ))}
          {filtered.length === 0 && <div className="text-center text-gray-400 py-4 text-sm">No commands found</div>}
        </div>
      </div>
    </div>
  );
}
