"use client";

interface ScanFinding {
  category: "secret_leak" | "unsafe_code" | "invalid_url" | "size_limit" | "known_vuln" | "policy";
  severity: "critical" | "high" | "medium" | "low" | "info";
  message: string;
  file_path: string | null;
  line_number: number | null;
  pattern_matched: string | null;
}

interface ScanResultData {
  app_id: string;
  passed: boolean;
  findings: ScanFinding[];
  files_scanned: number;
  total_bytes: number;
}

interface ContentScanReportProps {
  result: ScanResultData;
  appName: string;
}

const SEV_STYLES: Record<string, { label: string; color: string; icon: string }> = {
  critical: {
    label: "CRITICAL",
    color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300",
    icon: "🔴",
  },
  high: {
    label: "HIGH",
    color: "bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300",
    icon: "🟠",
  },
  medium: {
    label: "MEDIUM",
    color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300",
    icon: "🟡",
  },
  low: {
    label: "LOW",
    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300",
    icon: "🔵",
  },
  info: {
    label: "INFO",
    color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
    icon: "ℹ️",
  },
};

const CAT_LABELS: Record<string, string> = {
  secret_leak: "Secret Leak",
  unsafe_code: "Unsafe Code",
  invalid_url: "Invalid URL",
  size_limit: "Size Limit",
  known_vuln: "Known Vulnerability",
  policy: "Policy",
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

export function ContentScanReport({ result, appName }: ContentScanReportProps) {
  const criticals = result.findings.filter((f) => f.severity === "critical").length;
  const highs = result.findings.filter((f) => f.severity === "high").length;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Content Scan Report</h3>
          <p className="text-xs text-gray-500">
            {appName} • {result.files_scanned} files • {formatBytes(result.total_bytes)}
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${result.passed ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"}`}
        >
          {result.passed ? "✓ Passed" : "✗ Failed"}
        </span>
      </div>

      {/* Summary */}
      {result.findings.length > 0 && (
        <div className="flex gap-3 border-b border-gray-200 px-4 py-2 text-xs dark:border-gray-700">
          <span>{result.findings.length} findings</span>
          {criticals > 0 && <span className="font-medium text-red-600">{criticals} critical</span>}
          {highs > 0 && <span className="font-medium text-orange-600">{highs} high</span>}
        </div>
      )}

      {/* Findings */}
      {result.findings.length === 0 ? (
        <div className="py-6 text-center">
          <span className="text-3xl">🛡️</span>
          <p className="mt-2 text-sm text-gray-500">No issues found — clean scan</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {result.findings.map((f, i) => {
            const sev = SEV_STYLES[f.severity] ?? SEV_STYLES.info;
            return (
              <div key={i} className="px-4 py-2.5">
                <div className="flex items-center gap-2">
                  <span className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${sev.color}`}>
                    {sev.icon} {sev.label}
                  </span>
                  <span className="text-[10px] text-gray-400">
                    {CAT_LABELS[f.category] ?? f.category}
                  </span>
                </div>
                <p className="mt-0.5 text-xs">{f.message}</p>
                {(f.file_path || f.line_number) && (
                  <p className="mt-0.5 font-mono text-[10px] text-gray-400">
                    {f.file_path}
                    {f.line_number ? `:${f.line_number}` : ""}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
