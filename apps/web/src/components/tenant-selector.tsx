"use client";

interface Tenant { id: string; name: string; logo?: string; plan: string; }
interface TenantSelectorProps { tenants: Tenant[]; currentTenant: string; onSwitch: (id: string) => void; }

export function TenantSelector({ tenants, currentTenant, onSwitch }: TenantSelectorProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-gray-400">Organization</h3>
      <div className="space-y-1">
        {tenants.map(t => (
          <button key={t.id} onClick={() => onSwitch(t.id)}
            className={`flex w-full items-center gap-3 rounded-lg border p-2.5 text-left ${t.id === currentTenant ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <div className="flex h-8 w-8 items-center justify-center rounded bg-gray-200 text-sm font-bold dark:bg-gray-700">
              {t.name.charAt(0)}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-400">{t.plan}</p>
            </div>
            {t.id === currentTenant && <span className="text-xs text-blue-500">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
