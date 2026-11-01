"use client";

interface ContentViolation {
  violationType: string;
  severity: "low" | "medium" | "high" | "critical";
  field: string;
  message: string;
  suggestion?: string;
}

interface ValidationReport {
  passed: boolean;
  score: number;
  violations: ContentViolation[];
  warnings: string[];
}

const severityConfig: Record<string, { color: string; icon: string }> = {
  low: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "ℹ️" },
  medium: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⚠️" },
  high: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🚫" },
  critical: { color: "bg-red-200 text-red-800 dark:bg-red-900/40", icon: "🛑" },
};

export function ContentValidatorPanel({
  report,
  onRescan,
}: {
  report: ValidationReport;
  onRescan?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Content Validation</h2>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${report.passed ? "text-green-600" : "text-red-600"}`}>
            {report.passed ? "✅ Passed" : "❌ Failed"}
          </span>
          <span className="text-sm text-gray-500">Score: {report.score}/100</span>
          <button onClick={onRescan} className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">Rescan</button>
        </div>
      </div>

      <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${report.score >= 80 ? "bg-green-500" : report.score >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
          style={{ width: `${report.score}%` }} />
      </div>

      {report.violations.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Violations ({report.violations.length})</h3>
          {report.violations.map((v, i) => {
            const cfg = severityConfig[v.severity];
            return (
              <div key={i} className={`rounded-lg border-l-4 p-3 ${v.severity === "critical" ? "border-red-500" : v.severity === "high" ? "border-red-400" : v.severity === "medium" ? "border-yellow-400" : "border-gray-300"}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span>{cfg.icon}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{v.severity}</span>
                  <span className="text-xs text-gray-400">{v.violationType}</span>
                  <span className="text-xs text-gray-400">in {v.field}</span>
                </div>
                <p className="text-sm">{v.message}</p>
                {v.suggestion && <p className="text-xs text-gray-500 mt-1">💡 {v.suggestion}</p>}
              </div>
            );
          })}
        </div>
      )}

      {report.warnings.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold">Warnings</h3>
          {report.warnings.map((w, i) => (
            <div key={i} className="text-xs text-yellow-600 mt-1">⚠ {w}</div>
          ))}
        </div>
      )}
    </div>
  );
}
