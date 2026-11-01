"use client";

interface A11yIssue { rule: string; severity: string; message: string; }
interface A11yResult { component: string; issues: A11yIssue[]; passes: boolean; }
interface A11yReportCardProps { results: A11yResult[]; totalPassed: number; totalFailed: number; }

export function A11yReportCard({ results, totalPassed, totalFailed }: A11yReportCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">♿ Accessibility</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{totalPassed} passed</span>
          {totalFailed > 0 && <span className="text-red-500">{totalFailed} failed</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.component} className="px-4 py-2.5">
            <div className="flex items-center gap-2 text-sm">
              <span>{r.passes ? "✅" : "❌"}</span>
              <span className="font-medium">{r.component}</span>
            </div>
            {r.issues.map((issue, i) => (
              <p key={i} className="text-xs text-red-500 ml-6 mt-0.5">{issue.message}</p>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
