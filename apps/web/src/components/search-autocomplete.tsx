"use client";

interface Suggestion { text: string; type: string; icon: string; }
interface SearchAutocompleteProps { suggestions: Suggestion[];
  onSelect: (text: string) => void; visible: boolean; }

export function SearchAutocomplete({ suggestions, onSelect, visible }: SearchAutocompleteProps) {
  if (!visible || !suggestions.length) return null;
  return (
    <div className="absolute top-full left-0 right-0 mt-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl z-50 overflow-hidden">
      {suggestions.map((s, i) => (
        <button key={i} onClick={() => onSelect(s.text)}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 text-left">
          <span>{s.icon}</span>
          <span className="flex-1">{s.text}</span>
          <span className="text-xs text-gray-400 capitalize">{s.type}</span>
        </button>
      ))}
    </div>
  );
}
