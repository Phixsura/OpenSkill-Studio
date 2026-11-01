"use client";

interface TenantOverviewProps { totalTenants: number; active: number; suspended: number;
  totalUsers: number; totalStorageMb: number; }

export function TenantOverview({ totalTenants, active, suspended, totalUsers, totalStorageMb }: TenantOverviewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏢 Tenant Overview</h3>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Tenants", v: totalTenants }, { l: "Active", v: active },
          { l: "Suspended", v: suspended }, { l: "Users", v: totalUsers },
          { l: "Storage", v: `${totalStorageMb} MB` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
