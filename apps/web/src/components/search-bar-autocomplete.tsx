"use client";

import { useState } from "react";

interface Suggestion { label: string; icon: string; type: string; href: string; }
interface SearchBarAutocompleteProps { onSearch: (query: string) => { sections: Record<string, Suggestion[]>; total: number };
  onSelect: (href: string) => void; placeholder?: string; }

export function SearchBarAutocomplete({ onSearch, onSelect, placeholder = "Search..." }: SearchBarAutocompleteProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);
  const result = query.length >= 2 ? onSearch(query) : null;

  return (
    <div className="relative w-full max-w-md">
      <input value={query} onChange={e => setQuery(e.target.value)}
        onFocus={() => setFocused(true)} onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder={placeholder}
        className="w-full rounded-lg border px-4 py-2.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
      {focused && result && result.total > 0 && (
        <div className="absolute left-0 right-0 z-20 mt-1 rounded-lg border bg-white shadow-xl dark:bg-gray-900 dark:border-gray-700">
          {Object.entries(result.sections).map(([section, items]) => (
            <div key={section}>
              <p className="px-3 py-1 text-xs font-semibold text-gray-400 uppercase">{section}</p>
              {items.map((s, i) => (
                <button key={i} onClick={() => onSelect(s.href)}
                  className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
                  <span>{s.icon}</span><span>{s.label}</span>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
