"use client";

import { useState } from "react";

interface Command { id: string; label: string; shortcut: string; category: string; }
interface CommandPaletteModalProps { commands: Command[]; onSelect: (id: string) => void; onClose: () => void; }

export function CommandPaletteModal({ commands, onSelect, onClose }: CommandPaletteModalProps) {
  const [query, setQuery] = useState("");
  const filtered = query
    ? commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase()) || c.category.toLowerCase().includes(query.toLowerCase()))
    : commands;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-[20vh] z-50">
      <div className="w-full max-w-md rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-2xl overflow-hidden">
        <div className="p-3 border-b dark:border-gray-700">
          <input value={query} onChange={e => setQuery(e.target.value)} autoFocus
            placeholder="Type a command..."
            className="w-full px-3 py-2 text-sm bg-transparent outline-none" />
        </div>
        <div className="max-h-64 overflow-y-auto divide-y dark:divide-gray-700">
          {filtered.map(c => (
            <button key={c.id} onClick={() => onSelect(c.id)}
              className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 text-left">
              <div>
                <div className="text-sm">{c.label}</div>
                <div className="text-[10px] text-gray-400">{c.category}</div>
              </div>
              {c.shortcut && <kbd className="text-[10px] px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded font-mono">{c.shortcut}</kbd>}
            </button>
          ))}
          {filtered.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No commands found</div>}
        </div>
      </div>
    </div>
  );
}
