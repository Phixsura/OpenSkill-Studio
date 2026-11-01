"use client";

interface DocInfo { endpoint: string; method: string; coverage_score: number; fully_documented: boolean; }
interface Props { endpoints: DocInfo[]; coveragePct: number; fullyDocumentedCount: number; appName: string; }

export default function APIDeveloperAPIApiDocumentationCoverageCard({ endpoints, coveragePct, fullyDocumentedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Doc Coverage</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${coveragePct >= 80 ? "text-green-600" : coveragePct >= 50 ? "text-yellow-600" : "text-red-500"}`}>{coveragePct}%</span>
          <p className="text-[9px] text-gray-400">{fullyDocumentedCount}/{endpoints.length} complete</p>
        </div>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints registered</p>
      ) : (
        <div className="space-y-1">
          {endpoints.filter(e => !e.fully_documented).slice(0, 5).map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-500">{e.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.endpoint}</span>
              </div>
              <span className="text-orange-500">{e.coverage_score}/4</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
