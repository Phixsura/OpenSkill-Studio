"use client";

interface AnalysisInfo { query_id: string; depth: number; field_count: number; estimated_cost: number; has_introspection: boolean; warnings: string[]; }
interface Props { analyses: AnalysisInfo[]; expensiveCount: number; appName: string; }

export default function APIDeveloperAPIGraphQLQueryAnalyzerCard({ analyses, expensiveCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔮 GraphQL Analyzer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {expensiveCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{expensiveCount} expensive</span>}
      </div>
      {analyses.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No queries analyzed</p>
      ) : (
        <div className="space-y-1.5">
          {analyses.map((a) => (
            <div key={a.query_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${a.warnings.length > 0 ? "bg-orange-500" : "bg-green-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{a.query_id}</span>
              </div>
              <span className="text-gray-400">depth:{a.depth} cost:{a.estimated_cost}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
