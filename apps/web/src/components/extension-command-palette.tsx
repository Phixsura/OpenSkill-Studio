"use client";

import { useState, useMemo } from "react";

interface Command {
  id: string;
  label: string;
  icon: string;
  category: string;
  shortcut?: string;
  description?: string;
}

export function ExtensionCommandPalette({
  commands,
  isOpen,
  onSelect,
  onClose,
}: {
  commands: Command[];
  isOpen: boolean;
  onSelect?: (id: string) => void;
  onClose?: () => void;
}) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const filtered = useMemo(() => {
    if (!query) return commands;
    const q = query.toLowerCase();
    return commands.filter(
      (c) => c.label.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        (c.description || "").toLowerCase().includes(q)
    );
  }, [query, commands]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && filtered[selectedIndex]) {
      onSelect?.(filtered[selectedIndex].id);
      onClose?.();
    } else if (e.key === "Escape") {
      onClose?.();
    }
  };

  if (!isOpen) return null;

  const categories = [...new Set(filtered.map((c) => c.category))];

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/50" onClick={onClose}>
      <div className="w-full max-w-lg bg-white dark:bg-gray-900 rounded-xl shadow-2xl border dark:border-gray-700 overflow-hidden"
        onClick={(e) => e.stopPropagation()}>
        <div className="p-3 border-b dark:border-gray-700">
          <input type="text" value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
            onKeyDown={handleKeyDown}
            placeholder="Type a command..."
            autoFocus
            className="w-full bg-transparent border-none outline-none text-sm" />
        </div>

        <div className="max-h-80 overflow-y-auto p-1">
          {categories.map((cat) => (
            <div key={cat}>
              <div className="text-xs text-gray-400 uppercase px-3 py-1 mt-1">{cat}</div>
              {filtered.filter((c) => c.category === cat).map((cmd) => {
                const idx = filtered.indexOf(cmd);
                return (
                  <button key={cmd.id}
                    onClick={() => { onSelect?.(cmd.id); onClose?.(); }}
                    className={`w-full text-left flex items-center justify-between px-3 py-2 rounded-lg text-sm ${
                      idx === selectedIndex ? "bg-blue-100 dark:bg-blue-900/30" : "hover:bg-gray-100 dark:hover:bg-gray-800"
                    }`}>
                    <div className="flex items-center gap-2">
                      <span>{cmd.icon}</span>
                      <span>{cmd.label}</span>
                      {cmd.description && <span className="text-xs text-gray-400">— {cmd.description}</span>}
                    </div>
                    {cmd.shortcut && <kbd className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded font-mono">{cmd.shortcut}</kbd>}
                  </button>
                );
              })}
            </div>
          ))}
          {filtered.length === 0 && <div className="text-center text-gray-400 py-4 text-sm">No matching commands</div>}
        </div>
      </div>
    </div>
  );
}
