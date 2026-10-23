"use client";

interface SearchResult { name: string; category?: string; description?: string; install_count?: number; }
interface SearchResultsPageProps {
  query: string; results: SearchResult[]; total: number;
  page: number; totalPages: number; facets: Record<string, Record<string, number>>;
  onPageChange: (page: number) => void;
}

export function SearchResultsPage({ query, results, total, page, totalPages, facets, onPageChange }: SearchResultsPageProps) {
  return (
    <div>
      <h2 className="text-lg font-bold">Search: &quot;{query}&quot;</h2>
      <p className="text-sm text-gray-400">{total} results · Page {page}/{totalPages}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <div className="md:col-span-1">
          <h3 className="text-xs font-semibold text-gray-500">Categories</h3>
          {Object.entries(facets.categories || {}).map(([cat, count]) => (
            <p key={cat} className="text-xs text-gray-600">{cat} ({count})</p>
          ))}
        </div>
        <div className="md:col-span-3 space-y-2">
          {results.map((r, i) => (
            <div key={i} className="rounded border p-3 dark:border-gray-700">
              <h3 className="font-semibold text-sm">{r.name}</h3>
              <p className="text-xs text-gray-500">{r.description}</p>
            </div>
          ))}
        </div>
      </div>
      {totalPages > 1 && (
        <div className="mt-4 flex justify-center gap-2">
          <button onClick={() => onPageChange(page - 1)} disabled={page <= 1} className="rounded border px-3 py-1 text-sm disabled:opacity-30">←</button>
          <span className="px-3 py-1 text-sm">{page} / {totalPages}</span>
          <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} className="rounded border px-3 py-1 text-sm disabled:opacity-30">→</button>
        </div>
      )}
    </div>
  );
}
