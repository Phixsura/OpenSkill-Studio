"use client";

interface TenantUsage { tenantId: string; resources: Record<string, number>; totalUnits: number; }
interface TenantUsageMeterProps { tenants: TenantUsage[]; topResource: string;
  topTenants: { tenantId: string; usage: number }[]; }

export function TenantUsageMeter({ tenants, topResource, topTenants }: TenantUsageMeterProps) {
  const maxUsage = Math.max(...topTenants.map(t => t.usage), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Tenant Metering</h3>
        <span className="text-xs text-gray-400">{tenants.length} tenants</span>
      </div>
      <div className="p-4">
        <div className="text-xs text-gray-400 mb-2">Top by {topResource}</div>
        {topTenants.map(t => (
          <div key={t.tenantId} className="mb-1.5">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{t.tenantId}</span>
              <span className="text-gray-400">{t.usage}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${(t.usage / maxUsage) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
