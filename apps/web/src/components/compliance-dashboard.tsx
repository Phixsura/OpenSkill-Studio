"use client";

interface ComplianceRecord {
  developerId: string;
  developerName: string;
  status: "compliant" | "warning" | "violation" | "suspended";
  violations: number;
  warnings: number;
  hasAcceptedTos: boolean;
  lastReviewed?: string;
}

const statusConfig: Record<string, { color: string; icon: string; label: string }> = {
  compliant: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅", label: "Compliant" },
  warning: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⚠️", label: "Warning" },
  violation: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🚫", label: "Violation" },
  suspended: { color: "bg-gray-200 text-gray-600 dark:bg-gray-800", icon: "🔒", label: "Suspended" },
};

export function ComplianceDashboard({
  records,
  onSuspend,
  onRestore,
}: {
  records: ComplianceRecord[];
  onSuspend?: (id: string) => void;
  onRestore?: (id: string) => void;
}) {
  const byStatus = {
    compliant: records.filter((r) => r.status === "compliant").length,
    warning: records.filter((r) => r.status === "warning").length,
    violation: records.filter((r) => r.status === "violation").length,
    suspended: records.filter((r) => r.status === "suspended").length,
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📋 Developer Compliance</h2>

      <div className="grid grid-cols-4 gap-2">
        {Object.entries(byStatus).map(([status, count]) => {
          const cfg = statusConfig[status];
          return (
            <div key={status} className={`rounded-lg p-3 text-center ${cfg.color}`}>
              <span className="text-lg">{cfg.icon}</span>
              <span className="block text-xl font-bold">{count}</span>
              <span className="text-xs">{cfg.label}</span>
            </div>
          );
        })}
      </div>

      <div className="space-y-2">
        {records.map((rec) => {
          const cfg = statusConfig[rec.status];
          return (
            <div key={rec.developerId} className="rounded-xl border dark:border-gray-700 p-3 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">{rec.developerName}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                  {!rec.hasAcceptedTos && (
                    <span className="text-xs text-orange-500">⚠ ToS pending</span>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {rec.violations > 0 && <span className="text-red-500 mr-2">{rec.violations} violations</span>}
                  {rec.warnings > 0 && <span className="text-yellow-500">{rec.warnings} warnings</span>}
                </div>
              </div>
              <div>
                {rec.status !== "suspended" && rec.violations > 0 && (
                  <button onClick={() => onSuspend?.(rec.developerId)}
                    className="text-xs bg-red-600 text-white px-2 py-1 rounded">Suspend</button>
                )}
                {rec.status === "suspended" && (
                  <button onClick={() => onRestore?.(rec.developerId)}
                    className="text-xs bg-green-600 text-white px-2 py-1 rounded">Restore</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
