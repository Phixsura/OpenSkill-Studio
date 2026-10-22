"use client";

interface SearchResultsHeaderProps { query: string; total: number; page: number; totalPages: number; suggestion: string | null; }

export function SearchResultsHeader({ query, total, page, totalPages, suggestion }: SearchResultsHeaderProps) {
  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold">{total > 0 ? `Results for "${query}"` : `No results for "${query}"`}</h2>
      {total > 0 && <p className="text-sm text-gray-500">{total} result{total !== 1 ? "s" : ""} · Page {page}/{totalPages}</p>}
      {suggestion && <p className="mt-2 text-sm text-blue-600">💡 {suggestion}</p>}
    </div>
  );
}
