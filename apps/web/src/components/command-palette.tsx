"use client";

import { useState } from "react";

interface Command { id: string; label: string; shortcut?: string | null; category: string; icon: string; }
interface CommandPaletteProps { commands: Command[]; onSelect: (id: string) => void; onClose: () => void; }

export function CommandPalette({ commands, onSelect, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const filtered = query ? commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase())) : commands;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-24" onClick={onClose}>
      <div className="w-full max-w-lg rounded-lg bg-white shadow-2xl dark:bg-gray-800" onClick={e => e.stopPropagation()}>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Type a command..."
          autoFocus className="w-full border-b px-4 py-3 text-sm outline-none dark:border-gray-700 dark:bg-gray-800" />
        <ul className="max-h-64 overflow-y-auto p-1">
          {filtered.map(c => (
            <li key={c.id}>
              <button onClick={() => onSelect(c.id)}
                className="flex w-full items-center gap-3 rounded px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
                <span>{c.icon}</span>
                <span className="flex-1 text-left">{c.label}</span>
                {c.shortcut && <kbd className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">{c.shortcut}</kbd>}
              </button>
            </li>
          ))}
          {filtered.length === 0 && <li className="p-3 text-center text-sm text-gray-400">No commands found</li>}
        </ul>
      </div>
    </div>
  );
}
