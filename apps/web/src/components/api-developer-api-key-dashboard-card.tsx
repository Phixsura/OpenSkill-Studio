"use client";

interface DashInfo { total_keys: number; active_keys: number; expired_keys: number; revoked_keys: number; total_requests_today: number; keys_expiring_soon: number; }
interface Props { dashboard: DashInfo; appName: string; }

export default function APIDeveloperAPIKeyDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 API Key Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Active", v: d.active_keys, c: "text-green-600" },
          { l: "Expired", v: d.expired_keys, c: "text-yellow-600" },
          { l: "Revoked", v: d.revoked_keys, c: "text-red-500" },
          { l: "Total", v: d.total_keys, c: "text-gray-900 dark:text-gray-100" },
          { l: "Today", v: d.total_requests_today.toLocaleString(), c: "text-gray-900 dark:text-gray-100" },
          { l: "Expiring", v: d.keys_expiring_soon, c: d.keys_expiring_soon > 0 ? "text-orange-500" : "text-gray-900 dark:text-gray-100" },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className={`text-sm font-bold ${m.c}`}>{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
