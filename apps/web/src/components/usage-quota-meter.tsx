"use client";

interface Resource { resource: string; current: number; limit: number; unlimited: boolean; usage_pct: number; warning: boolean; exceeded: boolean; }
interface UsageQuotaMeterProps { plan: string; resources: Resource[]; onUpgrade: () => void; }

const labels: Record<string, string> = { api_calls: "API Calls", storage_mb: "Storage (MB)", webhooks: "Webhooks", team_members: "Team Members" };

export function UsageQuotaMeter({ plan, resources, onUpgrade }: UsageQuotaMeterProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Usage</h2>
        <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium capitalize text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{plan}</span>
      </div>
      <div className="space-y-3">
        {resources.map(r => (
          <div key={r.resource}>
            <div className="flex justify-between text-sm">
              <span>{labels[r.resource] ?? r.resource}</span>
              <span className="text-gray-400">
                {r.unlimited ? `${r.current.toLocaleString()} / ∞` : `${r.current.toLocaleString()} / ${r.limit.toLocaleString()}`}
              </span>
            </div>
            <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full transition-all ${r.exceeded ? "bg-red-500" : r.warning ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(r.usage_pct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
      {resources.some(r => r.warning) && (
        <button onClick={onUpgrade} className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white">
          Upgrade Plan
        </button>
      )}
    </div>
  );
}
