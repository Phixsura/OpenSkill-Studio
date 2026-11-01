"use client";

interface SearchResultInfo {
  entry_id: string;
  version: string;
  title: string;
  category: string;
  score: number;
  matched_fields: string[];
}

interface ChangelogSearchCardProps {
  query: string;
  results: SearchResultInfo[];
  totalIndexed: number;
  appName: string;
}

const CAT_COLORS: Record<string, string> = {
  added: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  fixed: "text-purple-700 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/30",
  changed: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  removed: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

export default function ChangelogSearchCard({
  query,
  results,
  totalIndexed,
  appName,
}: ChangelogSearchCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Changelog Search
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalIndexed} entries indexed</span>
      </div>

      {query && (
        <p className="mb-3 text-xs text-gray-500">
          {results.length} results for &ldquo;
          <span className="font-medium text-gray-800 dark:text-gray-200">{query}</span>&rdquo;
        </p>
      )}

      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">
          {query ? "No results found" : "Enter a search query"}
        </p>
      ) : (
        <div className="space-y-1.5">
          {results.map((r) => (
            <div
              key={r.entry_id}
              className="rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-gray-400">v{r.version}</span>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{r.title}</span>
                  {r.category && (
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${CAT_COLORS[r.category] ?? "bg-gray-100 text-gray-600"}`}
                    >
                      {r.category}
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-0.5 flex items-center gap-2 text-[10px] text-gray-400">
                <span>matched: {r.matched_fields.join(", ")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
