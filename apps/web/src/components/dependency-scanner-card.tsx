"use client";

interface ScanFinding {
  package_name: string;
  version: string;
  vuln_id: string;
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  fixable: boolean;
  fix_version: string | null;
}

interface ScanSummary {
  scanned_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  findings: ScanFinding[];
}

interface DependencyScannerCardProps {
  scan: ScanSummary;
  appName: string;
}

const SEVERITY_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  critical: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    label: "Critical",
  },
  high: {
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
    label: "High",
  },
  medium: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    label: "Medium",
  },
  low: {
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
    label: "Low",
  },
};

function SeverityBadge({ severity }: { severity: string }) {
  const st = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.low;
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${st.bg} ${st.text}`}>
      {st.label}
    </span>
  );
}

function SeverityCount({ label, count, color }: { label: string; count: number; color: string }) {
  if (count === 0) return null;
  return (
    <div className="text-center">
      <p className={`text-lg font-bold ${color}`}>{count}</p>
      <p className="text-[10px] text-gray-500">{label}</p>
    </div>
  );
}

export default function DependencyScannerCard({ scan, appName }: DependencyScannerCardProps) {
  const totalFindings = scan.findings.length;
  const allClear = totalFindings === 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Dependency Scan
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{scan.scanned_count} packages scanned</span>
      </div>

      {/* Summary counts */}
      <div className="mb-4 flex items-center justify-center gap-6">
        <SeverityCount
          label="Critical"
          count={scan.critical_count}
          color="text-red-600 dark:text-red-400"
        />
        <SeverityCount
          label="High"
          count={scan.high_count}
          color="text-orange-600 dark:text-orange-400"
        />
        <SeverityCount
          label="Medium"
          count={scan.medium_count}
          color="text-yellow-600 dark:text-yellow-400"
        />
        <SeverityCount
          label="Low"
          count={scan.low_count}
          color="text-blue-600 dark:text-blue-400"
        />
        {allClear && (
          <p className="text-sm font-medium text-green-600 dark:text-green-400">
            ✓ No vulnerabilities found
          </p>
        )}
      </div>

      {/* Findings list */}
      {totalFindings > 0 && (
        <div className="space-y-2">
          {scan.findings.map((f) => (
            <div
              key={f.vuln_id}
              className="flex items-start justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={f.severity} />
                  <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                    {f.package_name}@{f.version}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-gray-500">
                  {f.vuln_id} — {f.title}
                </p>
              </div>
              <div className="ml-3 shrink-0">
                {f.fixable ? (
                  <span className="text-xs text-green-600 dark:text-green-400">
                    Fix: {f.fix_version}
                  </span>
                ) : (
                  <span className="text-xs text-gray-400">No fix</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
