"use client";

interface TenantInfo { tenant_id: string; api_calls: number; webhook_deliveries: number; storage_bytes: number; total_cost_cents: number; }
interface Props { tenants: TenantInfo[]; totalCostCents: number; appName: string; }

function fmtCost(cents: number) { return `$${(cents / 100).toFixed(2)}`; }
function fmtStorage(b: number) { return b < 1_073_741_824 ? `${(b / 1_048_576).toFixed(1)}MB` : `${(b / 1_073_741_824).toFixed(1)}GB`; }

export default function APIDeveloperAPITenantUsageReportCard({ tenants, totalCostCents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏢 Tenant Usage Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {tenants.length} tenants</p>
        </div>
        <span className="text-sm font-bold text-green-600">{fmtCost(totalCostCents)}</span>
      </div>
      {tenants.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tenant data</p>
      ) : (
        <div className="space-y-2">
          {tenants.map((t) => (
            <div key={t.tenant_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{t.tenant_id}</span>
                <p className="text-[10px] text-gray-400">{t.api_calls.toLocaleString()} calls · {t.webhook_deliveries.toLocaleString()} webhooks</p>
              </div>
              <span className="text-[11px] font-medium text-gray-900 dark:text-gray-100">{fmtCost(t.total_cost_cents)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
