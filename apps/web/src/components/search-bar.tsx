"use client";

import { useState } from "react";

interface SearchBarProps { placeholder: string; shortcut: string; debounceMs: number;
  onSearch: (query: string) => void; suggestions?: string[];
  onSuggestionClick?: (suggestion: string) => void; }

export function SearchBar({ placeholder, shortcut, debounceMs, onSearch, suggestions,
  onSuggestionClick }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  const handleChange = (val: string) => {
    setQuery(val);
    onSearch(val);
  };

  return (
    <div className="relative">
      <div className="relative">
        <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
        <input value={query} onChange={e => handleChange(e.target.value)}
          onFocus={() => setFocused(true)} onBlur={() => setTimeout(() => setFocused(false), 200)}
          placeholder={placeholder}
          className="w-full rounded-lg border py-2.5 pl-10 pr-16 text-sm dark:border-gray-600 dark:bg-gray-700"
          onKeyDown={e => e.key === "Enter" && onSearch(query)} />
        <kbd className="absolute right-3 top-2 rounded border bg-gray-50 px-1.5 py-0.5 font-mono text-[10px] text-gray-400 dark:border-gray-600 dark:bg-gray-800">
          {shortcut}
        </kbd>
      </div>
      {focused && suggestions && suggestions.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
          {suggestions.map(s => (
            <button key={s} onMouseDown={() => { onSuggestionClick?.(s); setQuery(s); }}
              className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
              <span className="text-gray-400">🕐</span> {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
