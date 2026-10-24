"use client";

interface Violation { resourceId: string; tenants: string[]; severity: string; }
interface TenantIsolateReportProps { valid: boolean; violations: Violation[];
  tenantsChecked: number; resourcesChecked: number; }

export function TenantIsolateReport({ valid, violations, tenantsChecked, resourcesChecked }: TenantIsolateReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏢 Tenant Isolation</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Isolated" : `⚠ ${violations.length} violations`}
        </span>
      </div>
      <div className="flex gap-4 p-4 text-xs text-gray-400">
        <span>{tenantsChecked} tenants</span>
        <span>{resourcesChecked} resources</span>
      </div>
      {violations.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {violations.map(v => (
            <div key={v.resourceId} className="px-4 py-2 text-xs">
              <div className="text-red-600 font-mono">{v.resourceId}</div>
              <div className="text-gray-400">Shared by: {v.tenants.join(", ")}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
