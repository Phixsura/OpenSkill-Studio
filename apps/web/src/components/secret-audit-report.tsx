"use client";

interface SecretAuditResult { name: string; ageDays: number; daysUntilRotation: number; status: string; }
interface SecretAuditReportProps { total: number; compliant: number; compliancePct: number;
  maxAgeDays: number; results: SecretAuditResult[]; }

const STATUS_STYLE: Record<string, string> = {
  ok: "bg-green-100 text-green-700", warning: "bg-yellow-100 text-yellow-700",
  overdue: "bg-red-100 text-red-700",
};

export function SecretAuditReport({ total, compliant, compliancePct, maxAgeDays, results }: SecretAuditReportProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔑 Secret Rotation Audit</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${compliancePct === 100 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
          {compliancePct}% compliant
        </span>
      </div>
      <div className="flex gap-4 text-sm mb-4">
        <span>{compliant}/{total} secrets OK</span>
        <span className="text-gray-400">Max age: {maxAgeDays}d</span>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <div key={r.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div>
              <span className="text-sm font-mono">{r.name}</span>
              <span className="text-xs text-gray-400 ml-2">{r.ageDays}d old</span>
            </div>
            <span className={`text-xs px-1.5 py-0.5 rounded ${STATUS_STYLE[r.status] || ""}`}>{r.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
