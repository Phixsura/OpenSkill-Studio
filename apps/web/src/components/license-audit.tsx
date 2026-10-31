"use client";

interface LicenseDep { package: string; license: string; permissive: boolean; copyleft: boolean; risk: string; }
interface LicenseAuditProps { dependencies: LicenseDep[]; overallRisk: string; hasCopyleft: boolean;
  risks: Record<string, number>; }

const riskBadge: Record<string, string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export function LicenseAudit({ dependencies, overallRisk, hasCopyleft, risks }: LicenseAuditProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">License Audit</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${riskBadge[overallRisk] ?? ""}`}>{overallRisk} risk</span>
      </div>
      {hasCopyleft && <p className="text-xs text-yellow-600">⚠ Contains copyleft licenses</p>}
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {dependencies.map((d, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm font-mono">{d.package}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{d.license}</span>
              <span className={`rounded px-1.5 py-0.5 text-xs ${riskBadge[d.risk] ?? ""}`}>{d.risk}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
