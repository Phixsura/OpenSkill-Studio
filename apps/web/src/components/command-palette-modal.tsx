"use client";
import { useState } from "react";

interface Command { id: string; title: string; shortcut: string; category: string; icon: string; }
interface CommandPaletteModalProps { commands: Command[];
  onSelect: (id: string) => void; onSearch: (q: string) => void; }

export function CommandPaletteModal({ commands, onSelect, onSearch }: CommandPaletteModalProps) {
  const [query, setQuery] = useState("");
  const handleChange = (val: string) => { setQuery(val); onSearch(val); };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-lg w-full shadow-2xl">
      <div className="p-3 border-b dark:border-gray-700">
        <input value={query} onChange={e => handleChange(e.target.value)}
          placeholder="Type a command..." autoFocus
          className="w-full bg-transparent text-sm outline-none px-2 py-1" />
      </div>
      <div className="max-h-72 overflow-y-auto divide-y dark:divide-gray-700">
        {commands.map(c => (
          <button key={c.id} onClick={() => onSelect(c.id)}
            className="w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center gap-2">
              <span>{c.icon}</span>
              <span className="text-sm">{c.title}</span>
            </div>
            {c.shortcut && <kbd className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded font-mono">{c.shortcut}</kbd>}
          </button>
        ))}
      </div>
    </div>
  );
}
