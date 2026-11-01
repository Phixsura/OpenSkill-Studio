"use client";

interface ResultInfo { result_id: string; title: string; content_preview: string; result_type: string; relevance_score: number; }
interface Props { results: ResultInfo[]; totalIndexed: number; queryCount: number; appName: string; }

const tBadge: Record<string, string> = { endpoint: "bg-green-100 text-green-700", documentation: "bg-blue-100 text-blue-700", changelog: "bg-purple-100 text-purple-700", guide: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearchCard({ results, totalIndexed, queryCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔎 Portal Search</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalIndexed} indexed · {queryCount} queries</span>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No results</p>
      ) : (
        <div className="space-y-2">
          {results.map((r) => (
            <div key={r.result_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.title}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${tBadge[r.result_type] ?? ""}`}>{r.result_type}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400 truncate">{r.content_preview}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
