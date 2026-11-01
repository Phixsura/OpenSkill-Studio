"use client";

interface Finding { type: string; line: number; preview: string; severity: string; }
interface FileResult { filename: string; findings: Finding[]; count: number; }
interface SecretScannerReportProps { results: FileResult[]; totalFindings: number; filesScanned: number; clean: boolean; }

export function SecretScannerReport({ results, totalFindings, filesScanned, clean }: SecretScannerReportProps) {
  if (clean) {
    return (
      <div className="rounded-lg border border-green-500 bg-green-50 p-4 text-center dark:bg-green-900/10">
        <p className="text-lg">✅</p>
        <p className="text-sm font-medium text-green-700 dark:text-green-400">No secrets found in {filesScanned} files</p>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-red-600">🚨 Secrets Detected</h3>
        <span className="text-xs text-gray-400">{totalFindings} findings in {results.length} files</span>
      </div>
      {results.map((r, i) => (
        <div key={i} className="rounded-lg border border-red-300 p-3 dark:border-red-700">
          <p className="text-sm font-mono font-medium">{r.filename}</p>
          <div className="mt-2 space-y-1">
            {r.findings.map((f, j) => (
              <div key={j} className="flex items-center gap-2 text-xs">
                <span className="rounded bg-red-100 px-1.5 py-0.5 text-red-700 dark:bg-red-900/30 dark:text-red-400">{f.severity}</span>
                <span className="font-mono">{f.type}</span>
                <span className="text-gray-400">line {f.line}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
