"use client";

import { useState } from "react";

interface Command {
  commandId: string;
  title: string;
  category: string;
  description?: string;
  shortcut?: string;
}

export function CommandPaletteUI({
  commands,
  recentCommands,
  categories,
  onExecute,
  onSearch,
}: {
  commands: Command[];
  recentCommands: Command[];
  categories: string[];
  onExecute?: (commandId: string) => void;
  onSearch?: (query: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [catFilter, setCatFilter] = useState<string>("all");

  const handleSearch = (q: string) => {
    setQuery(q);
    onSearch?.(q);
  };

  const filtered = catFilter === "all" ? commands
    : commands.filter((c) => c.category === catFilter);

  return (
    <div className="space-y-3">
      <div className="relative">
        <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
        <input type="text" value={query} onChange={(e) => handleSearch(e.target.value)}
          placeholder="Type a command..."
          className="w-full rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 pl-9 pr-3 py-2.5 text-sm" />
      </div>

      {!query && recentCommands.length > 0 && (
        <div>
          <span className="text-xs text-gray-500">Recent</span>
          <div className="mt-1 space-y-0.5">
            {recentCommands.slice(0, 5).map((cmd) => (
              <button key={cmd.commandId} onClick={() => onExecute?.(cmd.commandId)}
                className="w-full text-left rounded-lg px-3 py-1.5 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-between">
                <span>{cmd.title}</span>
                <span className="text-xs text-gray-400">{cmd.category}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {categories.length > 1 && (
        <div className="flex gap-1 flex-wrap">
          <button onClick={() => setCatFilter("all")}
            className={`text-xs px-2 py-0.5 rounded-full ${catFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            All
          </button>
          {categories.map((cat) => (
            <button key={cat} onClick={() => setCatFilter(cat)}
              className={`text-xs px-2 py-0.5 rounded-full ${catFilter === cat ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              {cat}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-0.5 max-h-64 overflow-y-auto">
        {filtered.map((cmd) => (
          <button key={cmd.commandId} onClick={() => onExecute?.(cmd.commandId)}
            className="w-full text-left rounded-lg px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">{cmd.title}</span>
              {cmd.description && <span className="text-xs text-gray-400 ml-2">{cmd.description}</span>}
            </div>
            {cmd.shortcut && (
              <kbd className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded border dark:border-gray-700">{cmd.shortcut}</kbd>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
