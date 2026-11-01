"use client";

interface FindingInfo {
  finding_id: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low";
  description: string;
  remediated: boolean;
}

interface ComplianceAuditCardProps {
  findings: FindingInfo[];
  complianceScore: number;
  appName: string;
}

const SEV_STYLES: Record<string, { bg: string; text: string }> = {
  critical: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
  high: { bg: "bg-orange-100 dark:bg-orange-900/30", text: "text-orange-700 dark:text-orange-400" },
  medium: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
  low: { bg: "bg-blue-100 dark:bg-blue-900/30", text: "text-blue-700 dark:text-blue-400" },
};

export default function ComplianceAuditCard({
  findings,
  complianceScore,
  appName,
}: ComplianceAuditCardProps) {
  const openCount = findings.filter((f) => !f.remediated).length;
  const scoreColor =
    complianceScore >= 90
      ? "text-green-600 dark:text-green-400"
      : complianceScore >= 70
        ? "text-yellow-600"
        : "text-red-600 dark:text-red-400";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Compliance Audit
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${scoreColor}`}>{complianceScore}%</span>
          {openCount > 0 && <p className="text-[10px] text-red-500">{openCount} open</p>}
        </div>
      </div>

      {findings.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No findings</p>
      ) : (
        <div className="space-y-1.5">
          {findings.map((f) => {
            const sev = SEV_STYLES[f.severity] ?? SEV_STYLES.low;
            return (
              <div
                key={f.finding_id}
                className={`flex items-start gap-2 rounded px-2.5 py-1.5 ${f.remediated ? "opacity-50" : ""}`}
              >
                <span
                  className={`mt-0.5 rounded px-1 py-0.5 text-[9px] font-bold ${sev.bg} ${sev.text}`}
                >
                  {f.severity}
                </span>
                <div>
                  <span
                    className={`text-xs ${f.remediated ? "text-gray-400 line-through" : "text-gray-800 dark:text-gray-200"}`}
                  >
                    {f.description}
                  </span>
                  {f.remediated && <span className="ml-1 text-[10px] text-green-500">✓ fixed</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
