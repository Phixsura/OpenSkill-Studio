"use client";

interface SearchPageLayoutProps {
  query: string; resultCount: number; empty: boolean;
  suggestions: string[]; tips: string[];
  children: React.ReactNode;
}

export function SearchPageLayout({ query, resultCount, empty, suggestions, tips, children }: SearchPageLayoutProps) {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold">
          {empty ? `No results for "${query}"` : `Results for "${query}"`}
        </h1>
        {!empty && <p className="text-sm text-gray-400">{resultCount.toLocaleString()} apps found</p>}
      </div>
      {empty ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center dark:border-gray-700">
          <span className="text-4xl">🔍</span>
          <h2 className="mt-2 text-lg font-semibold">No apps found</h2>
          <ul className="mt-3 space-y-1">
            {tips.map((t, i) => <li key={i} className="text-sm text-gray-500">💡 {t}</li>)}
          </ul>
          {suggestions.length > 0 && (
            <p className="mt-3 text-sm">Did you mean: {suggestions.map((s, i) => (
              <span key={i} className="ml-1 text-blue-600 underline">{s}</span>
            ))}</p>
          )}
        </div>
      ) : (
        <div>{children}</div>
      )}
    </div>
  );
}
