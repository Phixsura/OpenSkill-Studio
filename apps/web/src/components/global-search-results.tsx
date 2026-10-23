"use client";

interface SearchResult { type: string; name?: string; title?: string; id?: string; }
interface GlobalSearchResultsProps { query: string; results: Record<string, SearchResult[]>; total: number; }

const TYPE_ICONS: Record<string, string> = { app: "📦", developer: "👨‍💻", doc: "📄" };

export function GlobalSearchResults({ query, results, total }: GlobalSearchResultsProps) {
  if (total === 0) return <p className="p-4 text-center text-sm text-gray-400">No results for &quot;{query}&quot;</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <p className="text-xs text-gray-400">{total} results for &quot;{query}&quot;</p>
      </div>
      {Object.entries(results).map(([type, items]) => items.length > 0 && (
        <div key={type} className="border-b p-2 last:border-0 dark:border-gray-700">
          <p className="px-2 text-xs font-medium text-gray-500 capitalize">{type}</p>
          {items.map((r, i) => (
            <div key={i} className="flex items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
              <span>{TYPE_ICONS[r.type] || "📌"}</span>
              <span>{r.name || r.title}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
