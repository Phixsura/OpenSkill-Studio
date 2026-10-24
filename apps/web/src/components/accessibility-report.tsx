"use client";

interface A11yResult { id: string; description: string; wcag: string; level: string; pass: boolean; details: string; }
interface AccessibilityReportProps { results: A11yResult[]; score: number; grade: string; passed: number; failed: number; }

const gradeColors: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600",
};

export function AccessibilityReport({ results, score, grade, passed, failed }: AccessibilityReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Accessibility Audit</h3>
        <div className="flex items-center gap-3">
          <span className={`text-2xl font-bold ${gradeColors[grade] ?? ""}`}>{grade}</span>
          <span className="text-sm text-gray-400">{score}%</span>
        </div>
      </div>
      <div className="flex gap-3 text-xs">
        <span className="text-green-600">✓ {passed} passed</span>
        <span className="text-red-600">✗ {failed} failed</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {results.map(r => (
          <div key={r.id} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={r.pass ? "text-green-600" : "text-red-600"}>{r.pass ? "✓" : "✗"}</span>
                <span className="text-sm">{r.description}</span>
              </div>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">WCAG {r.wcag} {r.level}</span>
            </div>
            {r.details && <p className="mt-1 ml-6 text-xs text-gray-500">{r.details}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
