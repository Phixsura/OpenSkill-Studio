"use client";

interface LimitCheck { resource: string; used: number; limit: number | string; pct: number; ok: boolean; warning?: boolean; }
interface UsageLimitBarProps { plan: string; checks: LimitCheck[];
  exceeded: boolean; nextPlan: string | null; onUpgrade: () => void; }

export function UsageLimitBar({ plan, checks, exceeded, nextPlan, onUpgrade }: UsageLimitBarProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📏 Plan Limits</h3>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 capitalize">{plan}</span>
      </div>
      <div className="space-y-2 mb-3">
        {checks.map(c => (
          <div key={c.resource}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{c.resource.replace("_", " ")}</span>
              <span className={!c.ok ? "text-red-500 font-medium" : "text-gray-400"}>
                {c.used} / {c.limit === "unlimited" ? "∞" : c.limit}
              </span>
            </div>
            {c.limit !== "unlimited" && (
              <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${!c.ok ? "bg-red-500" : c.warning ? "bg-yellow-500" : "bg-green-500"}`}
                     style={{ width: `${c.pct}%` }} />
              </div>
            )}
          </div>
        ))}
      </div>
      {exceeded && nextPlan && (
        <button onClick={onUpgrade}
          className="w-full py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          ⬆️ Upgrade to {nextPlan}
        </button>
      )}
    </div>
  );
}
