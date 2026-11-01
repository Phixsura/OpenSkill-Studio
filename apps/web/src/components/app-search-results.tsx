"use client";

interface SearchResult {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string;
  installCount: number;
}

interface AppSearchResultsProps {
  results: SearchResult[];
  loading?: boolean;
  query?: string;
}

export function AppSearchResults({ results, loading, query }: AppSearchResultsProps) {
  if (loading) return <p className="py-8 text-center text-sm text-gray-400">Searching...</p>;
  if (results.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-400">
      {query ? `No apps found for "${query}"` : "No apps available"}
    </p>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-500">{results.length} result{results.length !== 1 ? "s" : ""}{query ? ` for "${query}"` : ""}</p>
      {results.map(app => (
        <div key={app.id} className="rounded-lg border border-gray-200 p-4 hover:border-blue-300 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">{app.name}</h4>
            <span className="text-xs text-gray-500">📥 {app.installCount}</span>
          </div>
          {app.description && <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{app.description}</p>}
        </div>
      ))}
    </div>
  );
}
