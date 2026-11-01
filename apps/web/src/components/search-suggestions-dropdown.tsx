"use client";

interface Suggestion { type: string; text: string; id?: string; icon: string; }
interface SearchSuggestionsDropdownProps { suggestions: Suggestion[]; onSelect: (text: string) => void; visible: boolean; }

export function SearchSuggestionsDropdown({ suggestions, onSelect, visible }: SearchSuggestionsDropdownProps) {
  if (!visible || suggestions.length === 0) return null;
  return (
    <div className="absolute z-50 mt-1 w-full rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
      {suggestions.map((s, i) => (
        <button key={i} onClick={() => onSelect(s.text)}
          className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700">
          <span>{s.icon}</span>
          <span className="flex-1">{s.text}</span>
          <span className="text-xs text-gray-400">{s.type}</span>
        </button>
      ))}
    </div>
  );
}
