"use client";

interface DocResult { title: string; path: string; snippet: string; score: number; }
interface DocsSearchResultsProps { results: DocResult[]; query: string; total: number; }

export function DocsSearchResults({ results, query, total }: DocsSearchResultsProps) {
  return (
    <div className="space-y-3">
      <p className="text-xs text-gray-400">{total} result{total !== 1 ? "s" : ""} for &ldquo;{query}&rdquo;</p>
      {results.map((r, i) => (
        <a key={i} href={/^/(?!/)/.test(r.path) ? r.path : "#"} className="block rounded-lg border p-3 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
          <h4 className="text-sm font-semibold text-blue-600">{r.title}</h4>
          <p className="mt-0.5 text-xs text-gray-400 font-mono">{r.path}</p>
          <p className="mt-1 text-sm text-gray-500 line-clamp-2">{r.snippet}</p>
        </a>
      ))}
      {results.length === 0 && <p className="py-6 text-center text-sm text-gray-400">No docs found</p>}
    </div>
  );
}
