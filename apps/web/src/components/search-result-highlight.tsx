"use client";

interface SearchResultHighlightProps { title: string; highlightedTitle: string;
  snippet: string; matchCount: number; onClick: () => void; }

export function SearchResultHighlight({ title, highlightedTitle, snippet, matchCount, onClick }: SearchResultHighlightProps) {
  return (
    <button onClick={onClick}
      className="flex w-full flex-col gap-1 rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold" dangerouslySetInnerHTML={{ __html: highlightedTitle }} />
        <span className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-600 dark:bg-blue-900/20">
          {matchCount} match{matchCount !== 1 ? "es" : ""}
        </span>
      </div>
      <p className="text-xs text-gray-400 line-clamp-2">{snippet}</p>
    </button>
  );
}
