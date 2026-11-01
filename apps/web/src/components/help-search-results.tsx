"use client";

interface HelpResult { title: string; snippet: string; url: string; category: string; }
interface HelpSearchResultsProps { results: HelpResult[]; total: number; query: string; }

export function HelpSearchResults({ results, total, query }: HelpSearchResultsProps) {
  return (
    <div className="space-y-3">
      {total > 0 && <p className="text-xs text-gray-400">{total} results for &ldquo;{query}&rdquo;</p>}
      {results.map((r, i) => (
        <a key={i} href={r.url} className="block rounded-lg border dark:border-gray-700 p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
          <h4 className="text-sm font-semibold mb-1">{r.title}</h4>
          <p className="text-xs text-gray-500 line-clamp-2">{r.snippet}</p>
          {r.category && <span className="text-xs text-gray-400 mt-1 capitalize">{r.category}</span>}
        </a>
      ))}
      {total === 0 && query && <p className="text-sm text-gray-400 text-center py-8">No results found</p>}
    </div>
  );
}
