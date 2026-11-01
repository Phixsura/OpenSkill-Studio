"use client";

interface DocInfo { endpoint: string; method: string; coverage_pct: number; fully_documented: boolean; }
interface Props { docs: DocInfo[]; overallCoverage: number; undocumentedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverageCard({ docs, overallCoverage, undocumentedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Doc Coverage</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {docs.length} endpoints</p>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{overallCoverage}%</div>
          {undocumentedCount > 0 && <div className="text-[10px] text-amber-600 dark:text-amber-400">{undocumentedCount} incomplete</div>}
        </div>
      </div>
      <div className="mb-3 h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className={`h-2 rounded-full ${overallCoverage >= 80 ? "bg-green-500" : overallCoverage >= 50 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${overallCoverage}%` }} />
      </div>
      {docs.length > 0 && (
        <div className="space-y-1">
          {docs.map((d) => (
            <div key={`${d.method}-${d.endpoint}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{d.fully_documented ? "✅" : "📝"}</span>
                <span className="font-mono text-gray-500">{d.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{d.endpoint}</span>
              </div>
              <span className="text-gray-400">{d.coverage_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
