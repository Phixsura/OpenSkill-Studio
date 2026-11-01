"use client";

interface DependencyInfo {
  name: string;
  version: string;
  license: string;
  licenseRisk: "permissive" | "weak_copyleft" | "strong_copyleft" | "unknown";
  isOutdated: boolean;
  latestVersion: string;
  vulnCount: number;
  highestSeverity?: "low" | "medium" | "high" | "critical";
}

interface AuditSummary {
  passed: boolean;
  totalDeps: number;
  vulnsCritical: number;
  vulnsHigh: number;
  vulnsMedium: number;
  vulnsLow: number;
  licenseIssues: number;
  outdated: number;
}

const riskColors: Record<string, string> = {
  permissive: "text-green-600", weak_copyleft: "text-yellow-600",
  strong_copyleft: "text-red-600", unknown: "text-gray-500",
};

const sevColors: Record<string, string> = {
  low: "bg-gray-100 text-gray-600", medium: "bg-yellow-100 text-yellow-700",
  high: "bg-red-100 text-red-600", critical: "bg-red-200 text-red-800",
};

export function DepAuditPanel({
  summary,
  dependencies,
  onRescan,
}: {
  summary: AuditSummary;
  dependencies: DependencyInfo[];
  onRescan?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Dependency Audit</h2>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${summary.passed ? "text-green-600" : "text-red-600"}`}>
            {summary.passed ? "✅ Passed" : "❌ Failed"}
          </span>
          <button onClick={onRescan} className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">Rescan</button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Deps</span>
          <span className="font-bold text-lg">{summary.totalDeps}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Vulns</span>
          <span className="font-bold text-lg text-red-600">
            {summary.vulnsCritical + summary.vulnsHigh + summary.vulnsMedium + summary.vulnsLow}
          </span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">License</span>
          <span className={`font-bold text-lg ${summary.licenseIssues > 0 ? "text-red-600" : "text-green-600"}`}>
            {summary.licenseIssues}
          </span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Outdated</span>
          <span className="font-bold text-lg text-yellow-600">{summary.outdated}</span>
        </div>
      </div>

      <div className="space-y-1">
        {dependencies.map((dep) => (
          <div key={dep.name} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <code className="text-sm font-semibold">{dep.name}</code>
              <span className="text-xs text-gray-400">{dep.version}</span>
              {dep.isOutdated && <span className="text-xs text-yellow-600">→ {dep.latestVersion}</span>}
              <span className={`text-xs ${riskColors[dep.licenseRisk]}`}>{dep.license}</span>
            </div>
            <div className="flex items-center gap-1">
              {dep.vulnCount > 0 && dep.highestSeverity && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${sevColors[dep.highestSeverity]}`}>
                  {dep.vulnCount} vuln{dep.vulnCount > 1 ? "s" : ""}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
