"use client";

import { useState } from "react";

interface Suggestion { text: string; type: string; id: string; }
interface SearchAutocompleteProps { onSearch: (query: string) => void;
  suggestions: Suggestion[]; onSelect: (id: string) => void; placeholder?: string; }

export function SearchAutocomplete({ onSearch, suggestions, onSelect, placeholder }: SearchAutocompleteProps) {
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
          placeholder={placeholder ?? "Search apps..."} className="w-full rounded-lg border py-2.5 pl-10 pr-4 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      {focused && suggestions.length > 0 && (
        <div className="absolute z-10 mt-1 w-full rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
          {suggestions.map(s => (
            <button key={s.id} onMouseDown={() => { onSelect(s.id); setQuery(s.text); }}
              className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
              <span className="text-gray-400">{s.type === "app" ? "📦" : "🏷️"}</span>
              <span>{s.text}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
