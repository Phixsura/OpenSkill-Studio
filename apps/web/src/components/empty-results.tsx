"use client";

interface EmptyResultsProps { query?: string; suggestion?: string; }

export function EmptyResults({ query, suggestion }: EmptyResultsProps) {
  return (
    <div className="flex flex-col items-center py-12 text-center">
      <span className="text-5xl">🔍</span>
      <h3 className="mt-3 text-lg font-semibold text-gray-600">{query ? `No results for "${query}"` : "No results found"}</h3>
      {suggestion && <p className="mt-1 text-sm text-gray-400">{suggestion}</p>}
    </div>
  );
}
