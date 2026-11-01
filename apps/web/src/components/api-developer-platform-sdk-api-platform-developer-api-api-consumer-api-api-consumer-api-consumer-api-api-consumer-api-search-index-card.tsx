"use client";

interface Result { docId: string; docType: string; title: string; snippet: string; score: number; }
interface Props { results: Result[]; query: string; totalDocs: number; appName: string; }

const typeColors: Record<string, string> = {
  endpoint: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  webhook: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  changelog: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  doc: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndexCard({ results, query, totalDocs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔎 Search Index</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalDocs} documents indexed{query && ` · "${query}"`}</p>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">{query ? "No results found" : "Search the API"}</p>
      ) : (
        <div className="space-y-2">
          {results.slice(0, 6).map((r) => (
            <div key={r.docId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-2 text-[11px]">
                <span className={`rounded px-1 py-0.5 text-[9px] ${typeColors[r.docType] ?? ""}`}>{r.docType}</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.title}</span>
              </div>
              <div className="mt-0.5 truncate text-[10px] text-gray-400">{r.snippet}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
