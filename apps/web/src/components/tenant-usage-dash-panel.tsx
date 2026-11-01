"use client";
interface Usage { used: number; limit: number; pct: number; }
interface TenantUsageDashPanelProps { tenantId: string; plan: string; status: string;
  usage: Record<string, Usage>; }
const STATUS_STYLE: Record<string, string> = { ok: "text-green-600", warning: "text-yellow-600", exceeded: "text-red-500" };
export function TenantUsageDashPanel({ tenantId, plan, status, usage }: TenantUsageDashPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Tenant: {tenantId}</h3>
        <span className={`text-xs font-bold ${STATUS_STYLE[status] ?? ""}`}>{plan} · {status}</span>
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(usage).map(([name, u]) => (
          <div key={name}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{name.replace("_", " ")}</span>
              <span className="text-gray-400">{u.used.toLocaleString()}/{u.limit.toLocaleString()} ({u.pct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${u.pct >= 100 ? "bg-red-500" : u.pct >= 80 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(u.pct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
