"use client";

import { useState } from "react";

interface Command { id: string; label: string; shortcut: string | null; icon: string; category: string; }
interface CommandPaletteProps { commands: Command[]; onSelect: (id: string) => void; onClose: () => void; }

export function CommandPalette({ commands, onSelect, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const q = query.toLowerCase();
  const filtered = commands.filter(c => !q || c.label.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
  const groups = filtered.reduce<Record<string, Command[]>>((acc, c) => {
    (acc[c.category] ??= []).push(c); return acc;
  }, {});

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[20vh]" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl border bg-white shadow-2xl dark:bg-gray-900 dark:border-gray-700" onClick={e => e.stopPropagation()}>
        <input autoFocus type="text" placeholder="Type a command..." value={query} onChange={e => setQuery(e.target.value)}
          className="w-full border-b px-4 py-3 text-sm outline-none dark:bg-gray-900 dark:border-gray-700" />
        <div className="max-h-72 overflow-y-auto p-2">
          {Object.entries(groups).map(([cat, cmds]) => (
            <div key={cat}>
              <p className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">{cat}</p>
              {cmds.map(c => (
                <button key={c.id} onClick={() => onSelect(c.id)}
                  className="flex w-full items-center justify-between rounded px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
                  <span className="flex items-center gap-2"><span>{c.icon}</span>{c.label}</span>
                  {c.shortcut && <kbd className="text-xs text-gray-400 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{c.shortcut}</kbd>}
                </button>
              ))}
            </div>
          ))}
          {filtered.length === 0 && <p className="py-4 text-center text-sm text-gray-400">No commands found</p>}
        </div>
      </div>
    </div>
  );
}
