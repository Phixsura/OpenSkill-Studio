"use client";

interface Finding { severity: string; type: string; message: string; }

interface SecurityScanResultsProps {
  passed: boolean;
  riskLevel: string;
  findings: Finding[];
}

const SEVERITY_STYLES: Record<string, { icon: string; color: string }> = {
  high: { icon: "🔴", color: "text-red-700 dark:text-red-300" },
  medium: { icon: "🟡", color: "text-yellow-700 dark:text-yellow-300" },
  low: { icon: "🔵", color: "text-blue-700 dark:text-blue-300" },
};

export function SecurityScanResults({ passed, riskLevel, findings }: SecurityScanResultsProps) {
  return (
    <div className={`rounded-lg border p-4 ${passed ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"}`}>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold">{passed ? "✅ Security Scan Passed" : "⚠️ Security Issues Found"}</h4>
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs capitalize dark:bg-gray-800">Risk: {riskLevel}</span>
      </div>
      {findings.length === 0 ? (
        <p className="text-sm text-green-700 dark:text-green-300">No security issues detected</p>
      ) : (
        <ul className="space-y-1">
          {findings.map((f, i) => {
            const style = SEVERITY_STYLES[f.severity] ?? SEVERITY_STYLES.low;
            return (
              <li key={i} className={`text-sm ${style.color}`}>
                {style.icon} <span className="font-medium">[{f.severity.toUpperCase()}]</span> {f.message}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
