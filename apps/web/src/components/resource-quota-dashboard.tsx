"use client";

interface Quota { limit: number; unlimited: boolean; usage?: number; pctUsed?: number; }
interface ResourceQuotaDashboardProps { plan: string; quotas: Record<string, Quota & { usage: number }>; }

const ICONS: Record<string, string> = {
  api_calls: "📡", storage_mb: "💾", webhooks: "🔗", team_members: "👥", apps: "📦",
};

export function ResourceQuotaDashboard({ plan, quotas }: ResourceQuotaDashboardProps) {
  const entries = Object.entries(quotas);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Resource Quotas</h3>
        <span className="px-2 py-0.5 text-xs rounded bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 capitalize">{plan}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(([key, q]) => {
          const pct = q.unlimited ? 0 : Math.min(100, Math.round((q.usage / Math.max(q.limit, 1)) * 100));
          const color = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={key} className="px-4 py-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm">{ICONS[key] ?? "📦"} {key.replaceAll("_", " ")}</span>
                <span className="text-xs text-gray-400">
                  {q.unlimited ? "∞ unlimited" : `${q.usage.toLocaleString()} / ${q.limit.toLocaleString()}`}
                </span>
              </div>
              {!q.unlimited && (
                <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
