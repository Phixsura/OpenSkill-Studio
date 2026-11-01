"use client";

interface QuotaCheck { resource: string; used: number; limit: number | string;
  pct: number; exceeded: boolean; warning?: boolean; }
interface UsageQuotasCardProps { plan: string; checks: QuotaCheck[];
  anyExceeded: boolean; upgradeSuggested: boolean; }

const RESOURCE_LABEL: Record<string, string> = {
  api_calls: "API Calls", storage_mb: "Storage (MB)", apps: "Apps", webhooks: "Webhooks",
};

export function UsageQuotasCard({ plan, checks, anyExceeded, upgradeSuggested }: UsageQuotasCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 Usage Quotas</h3>
        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 capitalize">{plan}</span>
      </div>
      <div className="space-y-3">
        {checks.map(c => (
          <div key={c.resource}>
            <div className="flex justify-between text-sm mb-1">
              <span>{RESOURCE_LABEL[c.resource] || c.resource}</span>
              <span className={c.exceeded ? "text-red-600 font-medium" : "text-gray-500"}>
                {c.used.toLocaleString()} / {c.limit === "unlimited" ? "∞" : (c.limit as number).toLocaleString()}
              </span>
            </div>
            {c.limit !== "unlimited" && (
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${c.exceeded ? "bg-red-500" : c.warning ? "bg-yellow-500" : "bg-green-500"}`}
                     style={{ width: `${Math.min(c.pct, 100)}%` }} />
              </div>
            )}
          </div>
        ))}
      </div>
      {upgradeSuggested && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-blue-700 dark:text-blue-400">
          ⬆️ Consider upgrading your plan to increase limits
        </div>
      )}
    </div>
  );
}
