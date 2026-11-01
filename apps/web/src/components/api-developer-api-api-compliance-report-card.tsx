"use client";

interface FrameworkStats { compliant: number; non_compliant: number; pending: number; }
interface Props { frameworks: Record<string, FrameworkStats>; overallRate: number; nonCompliantCount: number; appName: string; }

export default function APIDeveloperAPIApiComplianceReportCard({ frameworks, overallRate, nonCompliantCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Compliance Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${overallRate >= 90 ? "text-green-600" : overallRate >= 70 ? "text-yellow-600" : "text-red-500"}`}>{overallRate}%</span>
          {nonCompliantCount > 0 && <p className="text-[9px] text-red-500">{nonCompliantCount} non-compliant</p>}
        </div>
      </div>
      {Object.keys(frameworks).length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compliance checks</p>
      ) : (
        <div className="space-y-2">
          {Object.entries(frameworks).map(([fw, stats]) => (
            <div key={fw} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <span className="text-[11px] font-bold text-gray-700 dark:text-gray-300">{fw}</span>
              <div className="flex gap-2 text-[10px]">
                <span className="text-green-600">{stats.compliant}✓</span>
                {stats.non_compliant > 0 && <span className="text-red-500">{stats.non_compliant}✗</span>}
                {stats.pending > 0 && <span className="text-gray-400">{stats.pending}?</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
