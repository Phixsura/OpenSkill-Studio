"use client";

interface Quota { resource: string; current: number; limit: number; pctUsed: number;
  exceeded: boolean; warning: boolean; }
interface QuotaEnforcePanelProps { quotas: Quota[]; exceeded: number;
  warnings: number; actionNeeded: boolean; }

export function QuotaEnforcePanel({ quotas, exceeded, warnings, actionNeeded }: QuotaEnforcePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Quota Enforcement</h3>
        <span className={`text-xs ${actionNeeded ? "text-red-500" : "text-green-600"}`}>
          {actionNeeded ? `⚠ ${exceeded} exceeded · ${warnings} warning` : "✅ All OK"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {quotas.map(q => (
          <div key={q.resource} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className={q.exceeded ? "text-red-600 font-bold" : q.warning ? "text-yellow-600" : ""}>{q.resource}</span>
              <span className="text-gray-400">{q.current}/{q.limit} ({q.pctUsed}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${q.exceeded ? "bg-red-500" : q.warning ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(q.pctUsed, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
