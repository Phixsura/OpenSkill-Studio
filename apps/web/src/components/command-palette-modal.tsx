"use client";

import { useState } from "react";

interface Command { id: string; label: string; shortcut: string | null; category: string; icon: string; }
interface CommandPaletteModalProps { commands: Command[]; onSelect: (id: string) => void; onClose: () => void; }

export function CommandPaletteModal({ commands, onSelect, onClose }: CommandPaletteModalProps) {
  const [query, setQuery] = useState("");
  const filtered = query
    ? commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase()))
    : commands;

  return (
    <div className="rounded-lg border bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900">
      <div className="border-b px-4 py-3 dark:border-gray-700">
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Type a command..."
          autoFocus className="w-full bg-transparent text-sm outline-none" />
      </div>
      <div className="max-h-64 overflow-y-auto p-2">
        {filtered.map(c => (
          <button key={c.id} onClick={() => { onSelect(c.id); onClose(); }}
            className="flex w-full items-center gap-3 rounded px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
            <span>{c.icon}</span>
            <span className="flex-1">{c.label}</span>
            {c.shortcut && <kbd className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-400 dark:bg-gray-800">{c.shortcut}</kbd>}
          </button>
        ))}
        {filtered.length === 0 && <p className="py-4 text-center text-sm text-gray-400">No commands found</p>}
      </div>
    </div>
  );
}
