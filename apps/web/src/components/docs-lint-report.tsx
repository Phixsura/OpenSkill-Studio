"use client";

interface LintResult { path: string; method: string; issueCount: number;
  errors: number; warnings: number; valid: boolean; }
interface DocsLintReportProps { results: LintResult[]; docScore: number;
  totalIssues: number; totalErrors: number; }

export function DocsLintReport({ results, docScore, totalIssues, totalErrors }: DocsLintReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Docs Lint</h3>
        <div className="flex gap-2 text-xs">
          <span className={docScore >= 80 ? "text-green-600" : "text-yellow-600"}>{docScore}% score</span>
          <span className="text-gray-400">{totalIssues} issues</span>
          {totalErrors > 0 && <span className="text-red-500">{totalErrors} errors</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={`${r.method}${r.path}`} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{r.valid ? "✅" : "❌"}</span>
              <span className="font-mono">{r.method} {r.path}</span>
            </div>
            <div className="flex gap-2 text-gray-400">
              {r.errors > 0 && <span className="text-red-500">{r.errors}E</span>}
              {r.warnings > 0 && <span className="text-yellow-600">{r.warnings}W</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
