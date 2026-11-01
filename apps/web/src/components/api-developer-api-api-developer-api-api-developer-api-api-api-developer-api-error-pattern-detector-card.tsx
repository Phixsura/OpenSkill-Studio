"use client";

interface PatternInfo { pattern_id: string; error_code: string; endpoint: string; occurrence_count: number; severity: string; affected_consumer_count: number; }
interface Props { patterns: PatternInfo[]; criticalCount: number; appName: string; }

const sevColor: Record<string, string> = { critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetectorCard({ patterns, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Error Patterns</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{criticalCount} critical</span>}
      </div>
      {patterns.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error patterns</p>
      ) : (
        <div className="space-y-1.5">
          {patterns.slice(0, 5).map((p) => (
            <div key={p.pattern_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${sevColor[p.severity] ?? ""}`}>{p.severity}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{p.error_code}</span>
                <span className="text-gray-400">{p.endpoint}</span>
              </div>
              <span className="text-gray-400">{p.occurrence_count}× · {p.affected_consumer_count} consumers</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
