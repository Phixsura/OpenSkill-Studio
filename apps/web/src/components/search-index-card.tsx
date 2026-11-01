"use client";

interface FacetInfo {
  value: string;
  count: number;
}

interface SearchIndexCardProps {
  docCount: number;
  docTypes: { type: string; count: number }[];
  recentSearches: { query: string; hits: number }[];
  appName: string;
}

export default function SearchIndexCard({
  docCount,
  docTypes,
  recentSearches,
  appName,
}: SearchIndexCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Search Index</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{docCount} documents</span>
      </div>

      {/* Doc types */}
      {docTypes.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 text-[10px] font-medium text-gray-500">Document Types</p>
          <div className="flex flex-wrap gap-1.5">
            {docTypes.map((t) => (
              <span
                key={t.type}
                className="rounded-full bg-blue-100 px-2 py-0.5 text-[11px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
              >
                {t.type} ({t.count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recent searches */}
      {recentSearches.length > 0 && (
        <div>
          <p className="mb-1 text-[10px] font-medium text-gray-500">Recent Searches</p>
          <div className="space-y-0.5">
            {recentSearches.map((s) => (
              <div key={s.query} className="flex items-center justify-between text-[11px]">
                <span className="text-gray-600 dark:text-gray-400">{s.query}</span>
                <span className="text-gray-400">{s.hits} hits</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {docTypes.length === 0 && recentSearches.length === 0 && (
        <p className="text-center text-sm text-gray-400">Empty index</p>
      )}
    </div>
  );
}
