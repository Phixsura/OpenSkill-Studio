"use client";

interface ViolationInfo {
  rule_id: string;
  rule_name: string;
  message: string;
  severity: "error" | "warning";
  field: string;
}

interface ComplianceReportCardProps {
  compliant: boolean;
  violations: ViolationInfo[];
  rulesChecked: number;
  appName: string;
}

export default function ComplianceReportCard({
  compliant,
  violations,
  rulesChecked,
  appName,
}: ComplianceReportCardProps) {
  const errors = violations.filter((v) => v.severity === "error");
  const warnings = violations.filter((v) => v.severity === "warning");

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{rulesChecked} rules checked</span>
          {compliant ? (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              ✓ Compliant
            </span>
          ) : (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              ✕ Non-compliant
            </span>
          )}
        </div>
      </div>

      {violations.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">
          All compliance checks passed
        </p>
      ) : (
        <div className="space-y-1.5">
          {errors.map((v) => (
            <div
              key={v.rule_id}
              className="flex items-start gap-2 rounded bg-red-50 px-2.5 py-1.5 dark:bg-red-950/20"
            >
              <span className="mt-0.5 text-xs text-red-500">✕</span>
              <div>
                <span className="text-xs font-medium text-red-700 dark:text-red-400">
                  {v.rule_name}
                </span>
                <p className="text-[11px] text-red-600/80 dark:text-red-400/70">{v.message}</p>
              </div>
            </div>
          ))}
          {warnings.map((v) => (
            <div
              key={v.rule_id}
              className="flex items-start gap-2 rounded bg-yellow-50 px-2.5 py-1.5 dark:bg-yellow-950/20"
            >
              <span className="mt-0.5 text-xs text-yellow-500">⚠</span>
              <div>
                <span className="text-xs font-medium text-yellow-700 dark:text-yellow-400">
                  {v.rule_name}
                </span>
                <p className="text-[11px] text-yellow-600/80 dark:text-yellow-400/70">
                  {v.message}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
