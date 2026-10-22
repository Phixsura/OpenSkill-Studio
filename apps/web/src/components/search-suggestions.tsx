"use client";

interface SearchSuggestionsProps { suggestions: string[]; onSelect: (suggestion: string) => void; visible: boolean; }

export function SearchSuggestions({ suggestions, onSelect, visible }: SearchSuggestionsProps) {
  if (!visible || suggestions.length === 0) return null;
  return (
    <div className="absolute z-20 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
      {suggestions.map(s => (
        <button key={s} onClick={() => onSelect(s)}
          className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800">{s}</button>
      ))}
    </div>
  );
}
