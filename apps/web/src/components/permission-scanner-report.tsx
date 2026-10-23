"use client";

interface Permission { permission: string; label: string; risk: string; reason: string; }
interface PermissionScannerReportProps { permissions: Permission[]; maxRisk: string; safeToInstall: boolean; }

const riskBadge: Record<string, string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  unknown: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
};

export function PermissionScannerReport({ permissions, maxRisk, safeToInstall }: PermissionScannerReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Permissions</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${safeToInstall ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {safeToInstall ? "Safe" : `Risk: ${maxRisk}`}
        </span>
      </div>
      <div className="space-y-2">
        {permissions.map(p => (
          <div key={p.permission} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{p.label}</p>
              <p className="text-xs text-gray-400">{p.reason}</p>
            </div>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${riskBadge[p.risk] ?? riskBadge.unknown}`}>
              {p.risk}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
