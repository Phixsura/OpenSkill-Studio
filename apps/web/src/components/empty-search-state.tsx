"use client";

interface EmptySearchStateProps { query: string; title: string; icon: string;
  suggestions: string[]; popularSearches: string[];
  onPopularSearch: (query: string) => void; onClearSearch: () => void; }

export function EmptySearchState({ query, title, icon, suggestions, popularSearches,
  onPopularSearch, onClearSearch }: EmptySearchStateProps) {
  return (
    <div className="mx-auto max-w-md space-y-6 py-12 text-center">
      <span className="text-5xl">{icon}</span>
      <h2 className="text-xl font-bold">{title}</h2>
      <div className="space-y-2 text-left">
        <p className="text-xs font-medium text-gray-400">Suggestions:</p>
        <ul className="space-y-1">
          {suggestions.map((s, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-gray-500">
              <span className="text-blue-400">→</span> {s}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <p className="text-xs font-medium text-gray-400">Popular searches:</p>
        <div className="mt-2 flex flex-wrap justify-center gap-2">
          {popularSearches.map(ps => (
            <button key={ps} onClick={() => onPopularSearch(ps)}
              className="rounded-full border px-3 py-1 text-xs hover:bg-blue-50 dark:border-gray-600 dark:hover:bg-blue-900/10">
              {ps}
            </button>
          ))}
        </div>
      </div>
      <button onClick={onClearSearch} className="text-sm text-blue-500 hover:underline">
        Clear search
      </button>
    </div>
  );
}
