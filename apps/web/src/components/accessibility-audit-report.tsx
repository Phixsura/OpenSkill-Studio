"use client";

interface Finding { id: string; level: string; description: string; passed: boolean; }
interface AccessibilityAuditReportProps { findings: Finding[]; score: number; grade: string;
  wcagACompliant: boolean; wcagAACompliant: boolean; }

const gradeColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };

export function AccessibilityAuditReport({ findings, score, grade, wcagACompliant, wcagAACompliant }: AccessibilityAuditReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Accessibility Audit</h2>
        <span className={`text-3xl font-black ${gradeColor[grade] ?? ""}`}>{grade}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{score}%</p><p className="text-xs text-gray-400">Score</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${wcagACompliant ? "text-green-600" : "text-red-600"}`}>
            {wcagACompliant ? "✓" : "✗"}
          </p><p className="text-xs text-gray-400">WCAG A</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${wcagAACompliant ? "text-green-600" : "text-red-600"}`}>
            {wcagAACompliant ? "✓" : "✗"}
          </p><p className="text-xs text-gray-400">WCAG AA</p>
        </div>
      </div>
      <div className="space-y-1">
        {findings.map(f => (
          <div key={f.id} className="flex items-center gap-2 rounded border px-3 py-1.5 dark:border-gray-700">
            <span className={f.passed ? "text-green-500" : "text-red-500"}>{f.passed ? "✓" : "✗"}</span>
            <span className="rounded bg-gray-100 px-1 py-0.5 text-[10px] dark:bg-gray-800">{f.level}</span>
            <span className="flex-1 text-sm">{f.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
