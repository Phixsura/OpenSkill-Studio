"use client";

interface TenantConfigInfo {
  key: string;
  value: string;
  overridden: boolean;
}

interface APITenantConfigCardProps {
  config: TenantConfigInfo[];
  tenantId: string;
  overrideCount: number;
  appName: string;
}

export default function APITenantConfigCard({ config, tenantId, overrideCount, appName }: APITenantConfigCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Tenant Config</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {tenantId}</p>
        </div>
        <span className="text-xs text-gray-400">{overrideCount} overrides</span>
      </div>

      {config.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No configuration</p>
      ) : (
        <div className="space-y-1">
          {config.map((c) => (
            <div key={c.key} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{c.key}</span>
                {c.overridden && <span className="rounded bg-blue-100 px-1 py-0.5 text-[8px] text-blue-600 dark:bg-blue-900 dark:text-blue-300">override</span>}
              </div>
              <span className="text-[11px] text-gray-400">{c.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
