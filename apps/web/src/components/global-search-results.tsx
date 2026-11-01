"use client";

interface SearchResult { id: string; title: string; category: string; snippet: string; }
interface GlobalSearchResultsProps { results: SearchResult[]; query: string; total: number;
  byCategory: Record<string, number>; onSelect: (id: string, category: string) => void; }

const catIcon: Record<string, string> = {
  apps: "📦", docs: "📚", settings: "⚙️", users: "👤", webhooks: "🔗",
};

export function GlobalSearchResults({ results, query, total, byCategory, onSelect }: GlobalSearchResultsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">
          {total} results for <strong>&quot;{query}&quot;</strong>
        </p>
        <div className="flex gap-2">
          {Object.entries(byCategory).map(([cat, count]) => (
            <span key={cat} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">
              {catIcon[cat] ?? "📁"} {cat} ({count})
            </span>
          ))}
        </div>
      </div>
      <div className="space-y-1.5">
        {results.map(r => (
          <button key={`${r.category}-${r.id}`} onClick={() => onSelect(r.id, r.category)}
            className="flex w-full items-start gap-3 rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <span className="text-lg">{catIcon[r.category] ?? "📁"}</span>
            <div>
              <p className="text-sm font-medium">{r.title}</p>
              <p className="text-xs text-gray-400">{r.category}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
